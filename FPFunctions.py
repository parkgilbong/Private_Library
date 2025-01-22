def FP_preprocessing_1ch(Tank_path:str, Dest_folder:str, FPS: int = 25, Rec_duration: int = 600, Namefor405: str = '405', Namefor465: str = '465'):
    """
    This function preprocesses the 1 channel(465) FP data from the tank file (raw data) and saves it as a .csv file.
        
    Parameters:
    Tank_path (str): Path to the tank file
    Dest_folder (str): Path to the folder where the .csv file will be saved
    FPS (int): Frames per second of the recording
    Rec_duration (int): Duration of the recording in seconds
    
    Returns:
    None
    """
    
    # Import necessary libraries
    import os
    import pandas as pd
    import numpy as  np
    import pylab as plt
    import PlotFunctions # import User-defined function 
    # import FileFunctions # import User-defined function
    from scipy.signal import butter, filtfilt
    from scipy.stats import linregress
    from scipy.optimize import curve_fit

    # import the tdt library
    import tdt

    ####################################################################################################################
    # 1. Load the data from the tank file
    ####################################################################################################################
    FPdata = tdt.read_block(Tank_path) # Read the data block from the tank file
    print(f'Data loaded successfully:{Tank_path}')

    CamTick = FPdata.epocs.PtC0.onset[0:(FPS*Rec_duration)] # 'FPS * Duration_sec' determines the length of CamTick
    ToffsetForCam = CamTick[0] # Get the initial timestamp
    corrected_CamTick = CamTick - ToffsetForCam # Adjust the CamTick to start from zero
    df_CamTick = pd.DataFrame({'original': CamTick,
                            'corrected': corrected_CamTick}) # Create a DataFrame for CamTick
    df_CamTick.to_csv('Data_CamTick.csv', header=True) # Save the DataFrame as a CSV file

    # export isosbestic and GCaMP signals
    control_whole = FPdata.streams['_405A'].data # Extract the control signal data
    signal_whole = FPdata.streams['_465A'].data # Extract the GCaMP signal data

    # create time array
    sampling_rate = FPdata.streams['_405A'].fs # Get the sampling rate
    time_seconds = np.linspace(1, len(control_whole), len(control_whole))/sampling_rate # Generate time array in seconds
    
    # Extract the time array for behavior data
    time_sec = time_seconds[np.min(np.where(time_seconds >= CamTick[0])) : np.max(np.where(time_seconds <= CamTick[(FPS*Rec_duration-1)]))]

    # Extract the raw control and signal data for the behavior period
    control_raw = control_whole[np.min(np.where(time_seconds >= CamTick[0])) : np.max(np.where(time_seconds <= CamTick[(FPS*Rec_duration-1)]))]
    signal_raw = signal_whole[np.min(np.where(time_seconds >= CamTick[0])) : np.max(np.where(time_seconds <= CamTick[(FPS*Rec_duration-1)]))]

    ####################################################################################################################
    # 2. Plot the raw signals
    ####################################################################################################################
    PlotFunctions.plot_sigle_line(x= time_sec,
                            y= control_raw,
                            Fig_size= (8,4),
                            Fig_title= Namefor405,
                            x_label= 'Time (sec)',
                            y_label= '(mV)',
                            x_lim= (None, None),
                            y_lim= (None, None),
                            colour= 'blue',
                            save= True)  
    PlotFunctions.plot_sigle_line(x= time_sec,
                            y= signal_raw,
                            Fig_size= (8,4),
                            Fig_title= Namefor465,
                            x_label= 'Time (sec)',
                            y_label= '(mV)',
                            x_lim= (None, None),
                            y_lim= (None, None),
                            colour= 'green',
                            save= True)  
    
    ylim_bottom = int(min([signal_raw.min(), control_raw.min()]))-5
    ylim_top = int(max([signal_raw.max(), control_raw.max()]))+5

    PlotFunctions.plot_dual_line(x = time_sec,
                            y1 = control_raw,
                            y2 = signal_raw,
                            Fig_size = (10,6),
                            Fig_title = f'Raw_signal_{Namefor465}',
                            x_label = 'Time (sec)',
                            y1_label = f'{Namefor405} (mV)',
                            y2_label = f'{Namefor465} (mV)',
                            x_lim = (None, None),
                            y1_lim = (ylim_bottom, ylim_top),
                            y2_lim = (ylim_bottom, ylim_top),
                            colour1 = 'blue',
                            colour2 = 'green',
                            save = True)
    
    ####################################################################################################################
    # 3. Smoothing the signals
    ####################################################################################################################
    # Lowpass filter - zero phase filtering (with filtfilt) is used to avoid distorting the signal.
    b,a = butter(3, 1, btype='low', fs=sampling_rate)
    signal_denoised = filtfilt(b,a, signal_raw)
    control_denoised = filtfilt(b,a, control_raw)
    # signal_denoised = signal_raw # if one may try to extract a raw trace (not smoothed), then use this variable.  
    # control_denoised = control_raw # if one may try to extract a raw trace (not smoothed), then use this variable. 

    # plot signals
    PlotFunctions.plot_dual_line(x = time_sec,
                            y1 = signal_denoised,
                            y2 = control_denoised,
                            Fig_size = (10,6),
                            Fig_title = 'Denoised_signals',
                            x_label = 'Time (sec)',
                            y1_label = f'{Namefor465}_denoised (mV)',
                            y2_label = f'{Namefor465}_denoised (mV)',
                            x_lim = (None, None),
                            y1_lim = (ylim_bottom, ylim_top),
                            y2_lim = (ylim_bottom, ylim_top),
                            colour1 = 'green',
                            colour2 = 'blue',
                            save = True)

    ####################################################################################################################
    # 4. The double exponential curve fitting b (photobleaching correction or detrending)
    ####################################################################################################################
    def double_exponential(t, const, amp_fast, amp_slow, tau_slow, tau_multiplier):
        '''Compute a double exponential function with constant offset.
        Parameters:
        t       : Time vector in seconds.
        const   : Amplitude of the constant offset. 
        amp_fast: Amplitude of the fast component.  
        amp_slow: Amplitude of the slow component.  
        tau_slow: Time constant of slow component in seconds.
        tau_multiplier: Time constant of fast component relative to slow. 
        '''
        tau_fast = tau_slow*tau_multiplier
        return const+amp_slow*np.exp(-t/tau_slow)+amp_fast*np.exp(-t/tau_fast)

    # Fit curve to GCaMP6f signal.
    max_sig = np.max(signal_denoised) 
    inital_params = [max_sig/2, max_sig/4, max_sig/4, 3600, 0.1]
    bounds = ([0      , 0      , 0      , 600  , 0],
            [max_sig, max_sig, max_sig, 36000, 1]) 
    signal_parms, parm_cov = curve_fit(double_exponential, time_sec, signal_denoised,
                                    p0=inital_params, bounds=bounds, maxfev=1000)

    signal_expfit = double_exponential(time_sec, *signal_parms)

    # Fit curve to Isosbestic signal.
    max_sig = np.max(control_denoised)
    inital_params = [max_sig/2, max_sig/4, max_sig/4, 3600, 0.1]
    bounds = ([0      , 0      , 0      , 600  , 0],
            [max_sig, max_sig, max_sig, 36000, 1])
    control_parms, parm_cov = curve_fit(double_exponential, time_sec, control_denoised, 
                                    p0=inital_params, bounds=bounds, maxfev=1000)

    control_expfit = double_exponential(time_sec, *control_parms)

    signal_detrended = signal_denoised - signal_expfit
    control_detrended = control_denoised - control_expfit

    ####################################################################################################################
    # 5. Motion correction
    ####################################################################################################################
    slope, intercept, r_value, p_value, std_err = linregress(x=control_detrended, y=signal_detrended)

    plt.scatter(control_detrended[::5], signal_detrended[::5],alpha=0.01, marker='.', color='green')
    x = np.array(plt.xlim())
    plt.plot(x, intercept+slope*x, color='k', linewidth=2)
    plt.xlabel(f'{Namefor405}')
    plt.ylabel(f'{Namefor465}')
    plt.title('Slope: {:.3f}'.format(slope) +'  ' + 'R^2: {:.3f}'.format(r_value**2))

    plt.savefig(f'Plot_{Namefor405}_{Namefor465}_correlation.png')

    print('Slope    : {:.3f}'.format(slope))
    print('R-squared: {:.3f}'.format(r_value**2))
    

    signal_est_motion = intercept + slope * control_detrended
    signal_corrected = signal_detrended - signal_est_motion

    ####################################################################################################################
    # 6. Normalize the signals
    ####################################################################################################################
    # compute dF/F and plot
    signal_dF_F = 100*signal_corrected/signal_expfit
    PlotFunctions.plot_sigle_line(x= time_sec,
                            y= signal_dF_F,
                            Fig_size= (10,6),
                            Fig_title= f'{Namefor465}_dFF',
                            x_label= 'Time (sec)',
                            y_label= f'{Namefor465} dF/F (%)',
                            x_lim= (None, None),
                            y_lim= (None, None),
                            colour= 'green',
                            save= True)
    
    # compute z-score and plot
    signal_zscored = (signal_corrected-np.mean(signal_corrected))/np.std(signal_corrected)
    PlotFunctions.plot_sigle_line(x= time_sec,
                            y= signal_zscored,
                            Fig_size= (10,6),
                            Fig_title= f'{Namefor465}_z-score',
                            x_label= 'Time (sec)',
                            y_label= f'{Namefor465} z-score',
                            x_lim= (None, None),
                            y_lim= (None, None),
                            colour= 'green',
                            save= True)

    ####################################################################################################################
    # 7. Save the data
    ####################################################################################################################
    GCaMP_signal = pd.DataFrame({'original_time': time_sec, 
                                'time': time_sec - ToffsetForCam,  
                                'value': signal_dF_F})
    GCaMP_signal.to_pickle('Final_table_raw_trace.pkl')
    GCaMP_signal.to_csv('Final_table_raw_trace.csv')
    
    # print('The file:Final_table_raw_trace.pkl saved successfully')

    return 

########################################################################################################################
########################################################################################################################
########################################################################################################################

def FP_preprocessing_2ch(Tank_path:str, Dest_folder:str, FPS: int = 25, Rec_duration: int = 600, Namefor405: str = '405', Namefor465: str = '465', Namefor560: str = '560'):
    """
    This function preprocesses the 2 channels (465, 560) FP data from the tank file (raw data) and saves it as a .csv file.
        
    Parameters:
    Tank_path (str): Path to the tank file
    Dest_folder (str): Path to the folder where the .csv file will be saved
    FPS (int): Frames per second of the recording
    Rec_duration (int): Duration of the recording in seconds
    
    Returns:
    None
    """
    
    # Import necessary libraries
    import os
    import pandas as pd
    import numpy as  np
    import pylab as plt
    import PlotFunctions # import User-defined function 
    # import FileFunctions # import User-defined function
    from scipy.signal import butter, filtfilt
    from scipy.stats import linregress
    from scipy.optimize import curve_fit

    # import the tdt library
    import tdt

    ####################################################################################################################
    # 1. Load the data from the tank file
    ####################################################################################################################
    FPdata = tdt.read_block(Tank_path) # Read the data block from the tank file
    print(f'Data loaded successfully:{Tank_path}')

    CamTick = FPdata.epocs.PtC0.onset[0:(FPS*Rec_duration)] # 'FPS * Duration_sec' determines the length of CamTick
    ToffsetForCam = CamTick[0] # Get the initial timestamp
    corrected_CamTick = CamTick - ToffsetForCam # Adjust the CamTick to start from zero
    df_CamTick = pd.DataFrame({'original': CamTick,
                            'corrected': corrected_CamTick}) # Create a DataFrame for CamTick
    df_CamTick.to_csv('Data_CamTick.csv', header=True) # Save the DataFrame as a CSV file

    # export isosbestic and GCaMP signals
    control_whole = FPdata.streams['_405A'].data # Extract the control signal data
    signal_whole = FPdata.streams['_465A'].data # Extract the GCaMP signal data
    signal2_whole = FPdata.streams['_560B'].data # Extract the RGECO signal data

    # create time array
    sampling_rate = FPdata.streams['_405A'].fs # Get the sampling rate
    time_seconds = np.linspace(1, len(control_whole), len(control_whole))/sampling_rate # Generate time array in seconds
    
    # Extract the time array for behavior data
    time_sec = time_seconds[np.min(np.where(time_seconds >= CamTick[0])) : np.max(np.where(time_seconds <= CamTick[(FPS*Rec_duration-1)]))]

    # Extract the raw control and signal data for the behavior period
    control_raw = control_whole[np.min(np.where(time_seconds >= CamTick[0])) : np.max(np.where(time_seconds <= CamTick[(FPS*Rec_duration-1)]))]
    signal_raw = signal_whole[np.min(np.where(time_seconds >= CamTick[0])) : np.max(np.where(time_seconds <= CamTick[(FPS*Rec_duration-1)]))]
    signal2_raw = signal2_whole[np.min(np.where(time_seconds >= CamTick[0])) : np.max(np.where(time_seconds <= CamTick[(FPS*Rec_duration-1)]))]

    ####################################################################################################################
    # 2. Plot the raw signals
    ####################################################################################################################
    PlotFunctions.plot_sigle_line(x= time_sec,
                            y= control_raw,
                            Fig_size= (8,4),
                            Fig_title= f'{Namefor405}',
                            x_label= 'Time (sec)',
                            y_label= f'{Namefor405} (mV)',
                            x_lim= (None, None),
                            y_lim= (None, None),
                            colour= 'blue',
                            save= True)  
    PlotFunctions.plot_sigle_line(x= time_sec,
                            y= signal_raw,
                            Fig_size= (8,4),
                            Fig_title= f'{Namefor465}',
                            x_label= 'Time (sec)',
                            y_label= f'{Namefor465} (mV)',
                            x_lim= (None, None),
                            y_lim= (None, None),
                            colour= 'green',
                            save= True)  
    PlotFunctions.plot_sigle_line(x= time_sec,
                             y= signal2_raw,
                             Fig_size= (8,4),
                             Fig_title= f'{Namefor560}',
                             x_label= 'Time (sec)',
                             y_label= f'{Namefor560} (mV)',
                             x_lim= (None, None),
                             y_lim= (None, None),
                             colour= 'red',
                             save= True)
    
    ylim_bottom = int(min([signal_raw.min(), control_raw.min()]))-5
    ylim_top = int(max([signal_raw.max(), control_raw.max()]))+5

    y2lim_bottom = int(min([signal2_raw.min(), control_raw.min()]))-5
    y2lim_top = int(max([signal2_raw.max(), control_raw.max()]))+5

    PlotFunctions.plot_dual_line(x = time_sec,
                            y1 = control_raw,
                            y2 = signal_raw,
                            Fig_size = (10,6),
                            Fig_title = f'Raw_signal_{Namefor465}',
                            x_label = 'Time (sec)',
                            y1_label = f'{Namefor405} (mV)',
                            y2_label = f'{Namefor465} (mV)',
                            x_lim = (None, None),
                            y1_lim = (ylim_bottom, ylim_top),
                            y2_lim = (ylim_bottom, ylim_top),
                            colour1 = 'blue',
                            colour2 = 'green',
                            save = True)
    PlotFunctions.plot_dual_line(x = time_sec,
                            y1 = control_raw,
                            y2 = signal2_raw,
                            Fig_size = (10,6),
                            Fig_title = f'Raw_signal_{Namefor560}',
                            x_label = 'Time (sec)',
                            y1_label = f'{Namefor405} (mV)',
                            y2_label = f'{Namefor560} (mV)',
                            x_lim = (None, None),
                            y1_lim = (y2lim_bottom, y2lim_top),
                            y2_lim = (y2lim_bottom, y2lim_top),
                            colour1 = 'blue',
                            colour2 = 'red',
                            save = True)
    
    ####################################################################################################################
    # 3. Smoothing the signals
    ####################################################################################################################
    # Lowpass filter - zero phase filtering (with filtfilt) is used to avoid distorting the signal.
    b,a = butter(3, 1, btype='low', fs=sampling_rate)
    signal_denoised = filtfilt(b,a, signal_raw)
    signal2_denoised = filtfilt(b,a, signal2_raw)
    control_denoised = filtfilt(b,a, control_raw)
    # signal_denoised = signal_raw # if one may try to extract a raw trace (not smoothed), then use this variable.  
    # control_denoised = control_raw # if one may try to extract a raw trace (not smoothed), then use this variable. 

    # plot signals
    PlotFunctions.plot_dual_line(x = time_sec,
                            y1 = signal_denoised,
                            y2 = control_denoised,
                            Fig_size = (10,6),
                            Fig_title = f'Denoised_signals_{Namefor465}',
                            x_label = 'Time (sec)',
                            y1_label = f'{Namefor465}_denoised (mV)',
                            y2_label = f'{Namefor405}_denoised (mV)',
                            x_lim = (None, None),
                            y1_lim = (ylim_bottom, ylim_top),
                            y2_lim = (ylim_bottom, ylim_top),
                            colour1 = 'green',
                            colour2 = 'blue',
                            save = True)
    PlotFunctions.plot_dual_line(x = time_sec,
                            y1 = signal2_denoised,
                            y2 = control_denoised,
                            Fig_size = (10,6),
                            Fig_title = f'Denoised_signals_{Namefor560}',
                            x_label = 'Time (sec)',
                            y1_label = f'{Namefor560}_denoised (mV)',
                            y2_label = f'{Namefor405}_denoised (mV)',
                            x_lim = (None, None),
                            y1_lim = (y2lim_bottom, y2lim_top),
                            y2_lim = (y2lim_bottom, y2lim_top),
                            colour1 = 'red',
                            colour2 = 'blue',
                            save = True)

    ####################################################################################################################
    # 4. The double exponential curve fitting b (photobleaching correction or detrending)
    ####################################################################################################################
    def double_exponential(t, const, amp_fast, amp_slow, tau_slow, tau_multiplier):
        '''Compute a double exponential function with constant offset.
        Parameters:
        t       : Time vector in seconds.
        const   : Amplitude of the constant offset. 
        amp_fast: Amplitude of the fast component.  
        amp_slow: Amplitude of the slow component.  
        tau_slow: Time constant of slow component in seconds.
        tau_multiplier: Time constant of fast component relative to slow. 
        '''
        tau_fast = tau_slow*tau_multiplier
        return const+amp_slow*np.exp(-t/tau_slow)+amp_fast*np.exp(-t/tau_fast)

    # Fit curve to GCaMP6f signal.
    max_sig = np.max(signal_denoised) 
    inital_params = [max_sig/2, max_sig/4, max_sig/4, 3600, 0.1]
    bounds = ([0      , 0      , 0      , 600  , 0],
            [max_sig, max_sig, max_sig, 36000, 1]) 
    signal_parms, parm_cov = curve_fit(double_exponential, time_sec, signal_denoised,
                                    p0=inital_params, bounds=bounds, maxfev=1000)

    signal_expfit = double_exponential(time_sec, *signal_parms)

    # Fit curve to RGECO signal.
    max_sig = np.max(signal2_denoised) 
    inital_params = [max_sig/2, max_sig/4, max_sig/4, 3600, 0.1]
    bounds = ([0      , 0      , 0      , 600  , 0],
              [max_sig, max_sig, max_sig, 36000, 1]) 
    signal2_parms, parm_cov = curve_fit(double_exponential, time_sec, signal2_denoised,
                                    p0=inital_params, bounds=bounds, maxfev=1000)
    
    signal2_expfit = double_exponential(time_sec, *signal2_parms)

    # Fit curve to Isosbestic signal.
    max_sig = np.max(control_denoised)
    inital_params = [max_sig/2, max_sig/4, max_sig/4, 3600, 0.1]
    bounds = ([0      , 0      , 0      , 600  , 0],
            [max_sig, max_sig, max_sig, 36000, 1])
    control_parms, parm_cov = curve_fit(double_exponential, time_sec, control_denoised, 
                                    p0=inital_params, bounds=bounds, maxfev=1000)

    control_expfit = double_exponential(time_sec, *control_parms)

    signal_detrended = signal_denoised - signal_expfit
    signal2_detrended = signal2_denoised - signal2_expfit
    control_detrended = control_denoised - control_expfit

    ####################################################################################################################
    # 5. Motion correction
    ####################################################################################################################
    slope, intercept, r_value, p_value, std_err = linregress(x=control_detrended, y=signal_detrended)

    plt.scatter(control_detrended[::5], signal_detrended[::5],alpha=0.005, marker='.', color='green')
    x = np.array(plt.xlim())
    plt.plot(x, intercept+slope*x, color='green', linewidth=2)
    plt.xlabel(f'{Namefor405}')
    plt.ylabel(f'{Namefor465} or {Namefor560}')
#     plt.title('Slope: {:.3f}'.format(slope) +'  ' + 'R^2: {:.3f}'.format(r_value**2))

    print('Slope    : {:.3f}'.format(slope))
    print('R-squared: {:.3f}'.format(r_value**2))
    

    signal_est_motion = intercept + slope * control_detrended
    signal_corrected = signal_detrended - signal_est_motion

    #560B signal
    slope2, intercept2, r_value2, p_value, std_err = linregress(x=control_detrended, y=signal2_detrended)

    plt.scatter(control_detrended[::5], signal2_detrended[::5],alpha=0.005, marker='.', color = 'red')
    x = np.array(plt.xlim())
    plt.plot(x, intercept2+slope2*x, color='red', linewidth=2)
#     plt.xlabel('ISOS')
#     plt.ylabel(f'{Namefor560}')
    plt.title('Slope: {:.3f}'.format(slope) +' ' + 'R^2: {:.3f}'.format(r_value**2) +"//" + 'Slope: {:.3f}'.format(slope2) +' ' + 'R^2: {:.3f}'.format(r_value2**2))
    
    plt.savefig(f'Plot_ISOS_{Namefor465}_or_{Namefor560}_correlation.png')
    
    print('Slope    : {:.3f}'.format(slope2))
    print('R-squared: {:.3f}'.format(r_value2**2))
    
    signal2_est_motion = intercept2 + slope2 * control_detrended
    signal2_corrected = signal2_detrended - signal2_est_motion

    ####################################################################################################################
    # 6. Normalize the signals
    ####################################################################################################################
    # compute dF/F and plot for 460B signal
    signal_dF_F = 100*signal_corrected/signal_expfit
    PlotFunctions.plot_sigle_line(x= time_sec,
                            y= signal_dF_F,
                            Fig_size= (10,6),
                            Fig_title= f'{Namefor465}_dFF',
                            x_label= 'Time (sec)',
                            y_label= f'{Namefor465} dF/F (%)',
                            x_lim= (None, None),
                            y_lim= (None, None),
                            colour= 'green',
                            save= True)
    
    # compute z-score and plot for 460B signal
    signal_zscored = (signal_corrected-np.mean(signal_corrected))/np.std(signal_corrected)
    PlotFunctions.plot_sigle_line(x= time_sec,
                            y= signal_zscored,
                            Fig_size= (10,6),
                            Fig_title= f'{Namefor465}_z-score',
                            x_label= 'Time (sec)',
                            y_label= f'{Namefor465} z-score',
                            x_lim= (None, None),
                            y_lim= (None, None),
                            colour= 'green',
                            save= True)
    
    # compute dF/F and plot for 560B signal
    signal2_dF_F = 100*signal2_corrected/signal2_expfit

    PlotFunctions.plot_sigle_line(x= time_sec,
                             y= signal2_dF_F,
                             Fig_size= (10,6),
                             Fig_title= f'{Namefor560}_dFF',
                             x_label= 'Time (sec)',
                             y_label= f'{Namefor560} dF/F (%)',
                             x_lim= (None, None),
                             y_lim= (None, None),
                             colour= 'red',
                             save= True)
    
    # compute z-score and plot for 560B signal
    signal2_zscored = (signal2_corrected-np.mean(signal2_corrected))/np.std(signal2_corrected)

    PlotFunctions.plot_sigle_line(x= time_sec,
                             y= signal2_zscored,
                             Fig_size= (10,6),
                             Fig_title= f'{Namefor560}_z-score',
                             x_label= 'Time (sec)',
                             y_label= f'{Namefor560} z-score',
                             x_lim= (None, None),
                             y_lim= (None, None),
                             colour= 'red',
                             save= True)
    
    ####################################################################################################################
    # 7. Save the data
    ####################################################################################################################
    GCaMP_signal = pd.DataFrame({'original_time': time_sec, 
                                'time': time_sec - ToffsetForCam,  
                                'value': signal_dF_F,
                                'value2': signal2_dF_F})
    GCaMP_signal.to_pickle('Final_table_raw_trace.pkl')
    GCaMP_signal.to_csv('Final_table_raw_trace.csv')
    
    # print('The file:Final_table_raw_trace.pkl saved successfully')

    return