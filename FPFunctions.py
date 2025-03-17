def FP_preprocessing_1ch(Tank_path:str, Dest_folder:str, Detrending_method:str = 'Exp_fit', Use_CamTick:bool = True, FPS: int = 25, Rec_duration: int = 600, Namefor405: str = '405', Namefor465: str = '465', SaveAsCSV:bool = False):
    """
    This function preprocesses the 1 channel(465) FP data from the tank file (raw data) and saves it as a .csv file.
        
    Parameters:
    Tank_path (str): Path to the tank file
    Dest_folder (str): Path to the folder where the .csv file will be saved
    Detrending_method (str): Method for detrending the signals. Options are 'Exp_fit' or 'Highpass_filter'. Default is 'Exp_fit'.
    Use_CamTick (bool): 
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
    import FileFunctions # import User-defined function
    from scipy.signal import butter, filtfilt
    from scipy.stats import linregress
    from scipy.optimize import curve_fit

    # import the tdt library
    import tdt

    FileFunctions.Set_WD(Dest_folder) # Set the working directory to the destination folder

    ####################################################################################################################
    # 1. Load the data from the tank file
    ####################################################################################################################
    FPdata = tdt.read_block(Tank_path) # Read the data block from the tank file
    print(f'Data loaded successfully:{Tank_path}')

    if Use_CamTick == True: 
        CamTick = FPdata.epocs.PtC0.onset[0:(FPS*Rec_duration)] # 'FPS * Duration_sec' determines the length of CamTick
        ToffsetForCam = CamTick[0] # Get the initial timestamp
        corrected_CamTick = CamTick - ToffsetForCam # Adjust the CamTick to start from zero
        df_CamTick = pd.DataFrame({'original': CamTick,
                                    'corrected': corrected_CamTick}) # Create a DataFrame for CamTick
        df_CamTick.to_csv('Data_CamTick.csv', header=True) # Save the DataFrame as a CSV file
    else:
        ToffsetForCam = 2 # Take a margin to remove the abnormal singal at the beginning of the recording

    # export isosbestic and GCaMP signals
    control_whole = FPdata.streams['_405A'].data # Extract the control signal data
    signal_whole = FPdata.streams['_465A'].data # Extract the GCaMP signal data

    # create time array
    sampling_rate = FPdata.streams['_405A'].fs # Get the sampling rate
    time_seconds = np.linspace(1, len(control_whole), len(control_whole))/sampling_rate # Generate time array in seconds
    
    if Use_CamTick == True:
        # Extract the time array for behavior data
        time_sec = time_seconds[np.min(np.where(time_seconds >= CamTick[0])) : np.max(np.where(time_seconds <= CamTick[(FPS*Rec_duration-1)]))]
        
        # Extract the raw control and signal data for the behavior period
        control_raw = control_whole[np.min(np.where(time_seconds >= CamTick[0])) : np.max(np.where(time_seconds <= CamTick[(FPS*Rec_duration-1)]))]
        signal_raw = signal_whole[np.min(np.where(time_seconds >= CamTick[0])) : np.max(np.where(time_seconds <= CamTick[(FPS*Rec_duration-1)]))]
    else: 
        inds = np.where(time_seconds > ToffsetForCam)
        ind = inds[0][0]
        time = time_seconds[ind:] # go from ind to final index
        control_raw = control_whole[ind:]
        signal_raw = signal_whole[ind:]
        time_sec = time_seconds[ind:] 

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

    PlotFunctions.plot_dual_line(x1 = time_sec,
                            y1 = control_raw,
                            x2 = time_sec,
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
    PlotFunctions.plot_dual_line(x1 = time_sec,
                            y1 = signal_denoised,
                            x2 = time_sec,
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
    # 4. Photobleaching correction (or detrending) using a double exponential curve fitting or High-pass filtering 
    ####################################################################################################################
    if Detrending_method == 'Exp_fit': 
    
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

    elif Detrending_method == 'Highpass_filter': 

        b,a = butter(2, 0.001, btype='high', fs=sampling_rate)
        signal_highpass = filtfilt(b,a, signal_denoised, padtype='even')
        control_highpass = filtfilt(b,a, control_denoised, padtype='even')

        signal_detrended = signal_highpass
        control_detrended = control_highpass

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
    if Detrending_method == 'Exp_fit':
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
    elif Detrending_method == 'Highpass_filter':
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
    if Detrending_method == 'Exp_fit':
        GCaMP_signal = pd.DataFrame({'original_time': time_sec, 
                                    'time': time_sec - ToffsetForCam,  
                                    'value': signal_dF_F,
                                    'value2': signal_corrected,
                                    'value3': signal_raw})
        
    elif Detrending_method == 'Highpass_filter':
        GCaMP_signal = pd.DataFrame({'original_time': time_sec, 
                                    'time': time_sec - ToffsetForCam,  
                                    'value': signal_zscored,
                                    'value2': signal_corrected,
                                    'value3': signal_raw})
    
    if SaveAsCSV == False:
        GCaMP_signal.to_pickle('Final_table_raw_trace.pkl')
    elif SaveAsCSV == True:
        GCaMP_signal.to_csv('Final_table_raw_trace.csv')
    
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
    import FileFunctions # import User-defined function
    from scipy.signal import butter, filtfilt
    from scipy.stats import linregress
    from scipy.optimize import curve_fit

    # import the tdt library
    import tdt

    FileFunctions.Set_WD(Dest_folder) # Set the working directory to the destination folder

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

    PlotFunctions.plot_dual_line(x1 = time_sec,
                            y1 = control_raw,
                            x2 = time_sec,
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
    PlotFunctions.plot_dual_line(x1 = time_sec,
                            y1 = control_raw,
                            x2 = time_sec,
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
    PlotFunctions.plot_dual_line(x1 = time_sec,
                            y1 = signal_denoised,
                            x2 = time_sec,
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
    PlotFunctions.plot_dual_line(x1 = time_sec,
                            y1 = signal2_denoised,
                            x2 = time_sec,
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
    
    # print('The file:Final_table_raw_trace.pkl saved successfully'

    return

########################################################################################################################
########################################################################################################################
########################################################################################################################

def Peak_Analysis(pkl_path:str = "Final_table_raw_trace.pkl", 
                prominence_thres:float = 2, 
                amplitude_thres:float = 4, 
                FPS:int = 25, 
                pre_window_len:int=3, 
                post_window_len:int=3,
                output_folder:str = "Peak_Analysis", 
                SavePlots:bool = False, 
                SaveData:bool = False, 
                SaveVideos:bool = False, 
                video_path:str = "video.avi"):
    '''
    This function performs peak analysis on the processed fluorescence data, identifying peaks based on prominence and amplitude thresholds, and extracting relevant information about these peaks.
    
    Parameters:
    pkl_path (str): Path to the pickle file containing the processed fluorescence data.
    FPS (int): Frames per second of the recording.
    prominence_thres (float): Threshold for the prominence of peaks.
    amplitude_thres (float): Threshold for the amplitude of peaks.
    pre_window_len (int): Length of the pre-peak window in seconds.
    post_winoow_len (int): Length of the post-peak window in seconds.
    SavePlots (bool): Whether to save the plots of the detected peaks.
    SaveData (bool): Whether to save the data of the detected peaks.
    SaveVideos (bool): Whether to save the videos of the detected peaks.
    
    Returns:
    None
    '''
    
    # Import necessary libraries
    import os
    import pandas as pd
    import numpy as  np
    import pylab as plt
    import VideoFunctions 
    from scipy.signal import find_peaks

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    os.chdir(output_folder)

    ####################################################################################################################
    # 1. Load the data
    ####################################################################################################################
    GCaMP_signal = pd.read_pickle(pkl_path) # Load the processed FP data
    time_sec = np.array(GCaMP_signal.time)  # Extract time data
    signal_dF_F = np.array(GCaMP_signal.value)  # Extract fluorescence signal data

    ####################################################################################################################
    # 2. Find the peaks
    ####################################################################################################################
    prominence_threshold = prominence_thres
    amplitude_threshold = amplitude_thres 

    # Find peaks in the dFF signal using the scipy.signal.find_peaks() function
    peaks, _ =find_peaks(x=signal_dF_F, prominence = prominence_threshold) #The prominence can be either 2 or 4.  
    PeakNum = len(peaks)
    
    if PeakNum == 0:
        print('No possible peaks detected in the signal')
        return
    
    else: 
        print(f'{PeakNum} possible peaks detected in the signal')
        # Function to find onset of the peak
        def find_peak_onset(signal, peak_index, threshold=0.0005):
            onset_index = peak_index
            while onset_index > 0 and signal[onset_index] > signal[onset_index - 1] - threshold:
                onset_index -= 1
            return onset_index

        # Find onset times for all peaks
        onset_indices = [find_peak_onset(signal_dF_F, peak) for peak in peaks]
        Amplitude = np.array(signal_dF_F[peaks]) - np.array(signal_dF_F[onset_indices])

        Final_peaks_indices = np.where(Amplitude > amplitude_threshold)
        if len(Final_peaks_indices[0]) == 0:
            print('No peaks detected with amplitude threshold')
            return
        
        else: 
            print(f'{len(Final_peaks_indices[0])} peaks detected with amplitude threshold')

            Final_peaks = peaks[Final_peaks_indices]
            Final_onset = [onset_indices[i] for i in Final_peaks_indices[0]]
            
            ####################################################################################################################
            # 3. Plot the peaks
            ####################################################################################################################
            # Plot the dF/F signal with the detected peaks and onsets
            fig1 = plt.figure(figsize=(16,9))
            ax1=fig1.add_subplot(311)
            plot1=ax1.plot(time_sec, signal_dF_F, 'g', label=r'$\Delta$F/F (%)')
            Peaks = ax1.plot(time_sec[Final_peaks], signal_dF_F[Final_peaks], label = 'peaks', color = 'r', marker='o', ls ='')
            Onsets = ax1.plot(time_sec[Final_onset], signal_dF_F[Final_onset], label='onsets', color = 'm', marker ='o', ls = "")

            # ax1.set_ylim(-10, 15)
            ax1.set_xlabel('Time (seconds)', fontsize =20)
            ax1.set_ylabel(r'$\Delta$F/F (%)', color='k', fontsize = 20)

            # ax1.set_title('Peak detection')
            # ax1.set_xlim(0, 600) # Set x-axis limit in seconds 

            lines = plot1 + Peaks + Onsets
            labels = [l.get_label() for l in lines]  #get legend labels
            legend = ax1.legend(lines, labels, loc='lower right', bbox_to_anchor=(1, 1), fontsize = 15) #add legend

            fig1.tight_layout()

            if SavePlots == True:
                plt.savefig('Plot_Peak_detection.png')

            plt.show()

            # Extract and save Ca2+ traces from 1 second before to 2 seconds after the detected peaks
            start_time_array = np.array(time_sec[Final_peaks])
            pre_window_length = pre_window_len
            post_window_length = post_window_len

            all_lines = []
            start_time_list = []
            end_time_list = []

            for time in start_time_array:
                start_time = time - pre_window_length
                end_time = time + post_window_length 
                filtered_data = np.array(GCaMP_signal.value[(time_sec >= start_time) & (time_sec <= end_time)].copy())

                # Adjust time to align data points
                filtered_data = filtered_data.copy() # Avoid SettingWithCopyWarning
            
                # Plot line (green with transparency)
                min_length = len(filtered_data)
                x_data = (np.linspace(0, pre_window_length + post_window_length, min_length))-pre_window_length
                y_data = filtered_data
            
                line, = plt.plot(x_data, y_data, color='green', alpha=0.1)
            
                all_lines.append(filtered_data)
                start_time_list.append(start_time)
                end_time_list.append(end_time)

            all_lines = pd.DataFrame(all_lines)
            all_lines_t = all_lines.transpose()

            data = all_lines.to_numpy()

            df_TimeWindow = pd.DataFrame({'start': start_time_list, 
                                        'end': end_time_list})

            mean_values = np.nanmean(data, axis=0)
            std_values = np.nanstd(data, axis=0)

            min_length = min(len(mean_values), len(std_values))
            x_data = (np.linspace(0, pre_window_length + post_window_length, min_length))-pre_window_length

            # Add graph title and labels
            plt.title('')
            plt.xlabel('Time (sec)')
            plt.ylabel(r'$\Delta$F/F (%)')

            # plt.legend()
            plt.grid(True)
            plt.ylim(-5, 10)
            plt.xlim(-pre_window_length, post_window_length)
            plt.axvline(x=0, color = "red", linestyle = '--', linewidth = 1)

            plt.plot(x_data, mean_values, color='green', label='Mean Value', linewidth=4)

            if SavePlots == True:
                plt.savefig('Plot_Peak_extraction.png')

            plt.show()

            if SaveData == True:
                all_lines_t.to_pickle(f'Data_Extraced_signal_of_detected_peaks.pkl')
                df_TimeWindow.to_pickle(f'Data_TimeWindow_for_detected_peaks.pkl')

            ####################################################################################################################
            # 4. Save the data
            ####################################################################################################################
            # Save detected peaks information as DataFrame 
            df_peaks = pd.DataFrame(data={'Peak_Index': Final_peaks,
                                        'Peak_X': np.array(time_sec[Final_peaks]), 
                                        'Peak_Y': np.array(signal_dF_F[Final_peaks]),
                                        'FrameForPeak': np.int64((time_sec[Final_peaks])*FPS),
                                        'Onset_Index': np.array(Final_onset),
                                        'Onset_X': np.array(time_sec[Final_onset]),
                                        'Onset_Y': np.array(signal_dF_F[Final_onset]),
                                        'FrameForOnset': np.int64((time_sec[Final_onset])*FPS),
                                        'OnsetLatency': np.subtract(np.array(time_sec[Final_peaks]), np.array(time_sec[Final_onset])),
                                        'Height': np.subtract(np.array(signal_dF_F[Final_peaks]), np.array(signal_dF_F[Final_onset]))})

            print('Number of peaks detected:', len(df_peaks.Peak_Index))
            print('Mean amplitude of peaks:', df_peaks.Height.mean())
            print('Mean latency of peaks:', df_peaks.OnsetLatency.mean())

            if SaveData == True:
                df_peaks.to_csv('Data_Peak_detection.csv', header=True)

            ####################################################################################################################
            # 5. Save the videos
            ####################################################################################################################
            if SaveVideos == True:
                slices_df = pd.DataFrame({'start_frame': df_peaks.FrameForPeak - pre_window_length*FPS,
                                        'end_frame': df_peaks.FrameForPeak + post_window_length*FPS})
            
                VideoFunctions.extract_video_slices(video_path= video_path,
                                            slices_df= slices_df,
                                            output_folder= 'spike_detection')
            return

########################################################################################################################
########################################################################################################################
########################################################################################################################

def Epoch_Analysis_3EVT(pkl_path:str = "Final_table_raw_trace.pkl",
                evt_path:str = "Data_DLC.csv",
                PRE_TIME:int = 5,
                POST_TIME:int = 10,
                FPS:int = 25,
                Rec_duration:int = 600,
                SavePlots:bool = False,
                SaveData:bool = False,
                output_folder:str = "Epoch_Analysis"):
    '''
    This function performs epoch analysis on the processed fluorescence data, aligning the data to behavioral events and extracting relevant information about these epochs.

    Parameters:
    pkl_path (str): Path to the pickle file containing the processed fluorescence data.
    evt_path (str): Path to the CSV file containing the behavioral events data.
    Pre_window_len (int): Length of the pre-event window in seconds.
    Post_window_len (int): Length of the post-event window in seconds.
    FPS (int): Frames per second of the recording.
    Rec_duration (int): Duration of the recording in seconds.
    SavePlots (bool): Whether to save the plots of the detected epochs.
    SaveData (bool): Whether to save the data of the detected epochs.

    Returns:
    None

    '''

    ####################################################################################################################
    # 1. Import necessary libraries
    ####################################################################################################################
    import os
    import pandas as pd
    import numpy as  np
    import pylab as plt
    from matplotlib.patches import Patch
    
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # os.chdir(output_folder)

    ####################################################################################################################
    # 2. Load the data
    ####################################################################################################################
    GCaMP_signal = pd.read_pickle(pkl_path)
    time_sec = GCaMP_signal.time
    signal_dF_F = GCaMP_signal.value

    df_EVT = pd.read_csv(evt_path, header=0, index_col=0)

    ####################################################################################################################
    # 3. Generate plots of the fluorescence signal aligned to behavioral events
    ####################################################################################################################
    # Generate time series of behavioral data
    CamTickTime = np.linspace(0, Rec_duration, Rec_duration*FPS)

    # First make a continous time series of social events
    # Event1 index == 1이면 Nose-to-Snout interaction ON, Event1 index == 2이면 Nose-to-Snout interaction OFF.
    if 'EVT1' in df_EVT.columns: 
        S_interaction_ON = np.array(CamTickTime[df_EVT.EVT1 == 1])
        S_interaction_OFF = np.array(CamTickTime[df_EVT.EVT1 == 2])

    # If Event2_index == 1, else -> S_zone entry, if EVT2 == 2, S_zone -> else exit.
    S_zone_in = np.array(CamTickTime[df_EVT.EVT2 == 1]) 
    # S_zone_in = np.insert(S_zone_in,0,CamTick[0]) # Adjust the index of Frame0 arbitrarily if starting from S_zone.
    S_zone_out = np.array(CamTickTime[df_EVT.EVT2 == 2]) 

    # Similarly for E-zone. If EVT3 == 1, else -> E-zone, if EVT3 == 2, E-zone -> else
    E_zone_in = np.array(CamTickTime[df_EVT.EVT3 == 1])
    E_zone_out = np.array(CamTickTime[df_EVT.EVT3 == 2])

    Evt_x = np.append(np.append(time_sec[0], np.reshape(np.kron([S_interaction_ON, S_interaction_OFF],
                    np.array([[1], [1]])).T, [1,-1])[0]), np.array(time_sec)[-1])
    sz = len(S_interaction_ON)

    CamTick = []

    for i in range(len(S_interaction_ON)):
        CamTick.append(1)

    # Create a vertical stack of arrays: two arrays of zeros('np.zeros(sz)') and two arrays of ones (d')
    # Then, transpose the stacked array and reshaping it. 
    # Append '0' at the start and end of the reshaped array
    Evt_y = np.append(np.append(0, np.reshape(np.vstack([np.zeros(sz), CamTick, CamTick, np.zeros(sz)]).T, [1, -1])[0]), 0)

    y_scale = 3
    y_offset = -10

    # First subplot in a series: dFF with social epocs
    fig1 = plt.figure(figsize=(10,6))
    ax1 = fig1.add_subplot(211)

    p1, = ax1.plot(time_sec, signal_dF_F, label='GCaMP', linewidth=1, color='green')
    p2, = ax1.plot(Evt_x, y_scale*Evt_y+y_offset, linewidth=1, color='dodgerblue', label='Nose-to-Snout')
    ax1.set_ylim(-10, 10)
    ax1.set_xlim(0, 600)
    ax1.set_ylabel(r'$\Delta$F/F (%)')
    ax1.set_xlabel('Time (sec)')
    ax1.set_title('dFF when Nose-to-Snout interaction')
    ax1.legend(handles=[p1,p2], loc='lower right', bbox_to_anchor=(1.1, 1))
    fig1.tight_layout()

    # plt.show()

    # Create the plot
    # fig3 = plt.figure(figsize=(10,6))
    ax2 = fig1.add_subplot(212)

    # Create the line plot
    p1, = ax2.plot(time_sec, signal_dF_F,linewidth=1, color='green', label='GCaMP')

    # Add the vertical spnas using 'axvspan'.
    for on, off in zip(S_zone_in, S_zone_out):
        ax2.axvspan(on, off, alpha=0.25, color='dodgerblue')
    for on, off in zip(E_zone_in, E_zone_out):
        ax2.axvspan(on, off, alpha=0.25, color='orange')
    ax2.set_ylim(-10, 15)
    ax2.set_xlim(0, 600)
    ax2.set_ylabel(r'$\Delta$F/F (%)')
    ax2.set_xlabel('Time (sec)')
    ax2.set_title('dFF with ROI segmentation')

    # Create a custom legend for the vertical spans. 
    handles, labels = ax2.get_legend_handles_labels()
    handles.append(Patch(color='dodgerblue', alpha=0.25, label='S-zone'))
    handles.append(Patch(color='orange', alpha=0.25, label='E-zone'))

    ax2.legend(handles=handles, loc='lower right',bbox_to_anchor=(1.1, 1))

    fig1.tight_layout()

    if SavePlots == True: 
        fig1.savefig(os.path.join(output_folder, 'Plot_dFF_with_ROI_segmentation.png'))

    plt.show()

    ####################################################################################################################
    # 4. Extract the signals for the EVT1 epoch
    ####################################################################################################################
    EVTtype = 'EVT1' # Selected event
    selected_event = 1.0 # '1' means the onset time of the event.

    # Filter rows corresponding to the selected event
    selected_events_data = df_EVT[df_EVT[EVTtype] == selected_event].copy() #SettingWithCopyWarning 참고 
    selected_events_data['EVT_time'] = list((selected_events_data.index+1)/FPS)

    # Create the plot
    fig2 =plt.figure(figsize=(6, 10))
    ax2 = fig2.add_subplot(211)

    # Extract data for each event and plot as lineplot
    all_lines = [] 

    # Variables to store start_time and end_time 
    start_time_list = []
    end_time_list = []

    pre_window_length = PRE_TIME
    post_window_length = POST_TIME 

    # List to store all lines
    for index, row in selected_events_data.iterrows():
        selected_event_time = row['EVT_time']

        # Extract data from 5 seconds before to 10 seconds after the event time
        start_time = selected_event_time - pre_window_length
        end_time = selected_event_time + post_window_length
        filtered_data = GCaMP_signal[(GCaMP_signal['time'] >= start_time) & (GCaMP_signal['time'] <= end_time)]

        # Adjust the time to align the data points
        filtered_data = filtered_data.copy() #Refer to SettingWithCopyWarning 
        filtered_data['time'] -= selected_event_time

        # Plot lineplot (in green with adjusted transparency)
        x_data = filtered_data['time']
        y_data = filtered_data['value']
        
        p1, = ax2.plot(x_data, y_data, color=[.7, .7, .7], linewidth=.5, label='Individual Trials')
        all_lines.append(y_data.values)  # Store data points at each time point
        start_time_list.append(start_time)
        end_time_list.append(end_time)

    # Convert data points at each time point to a 2D array
    all_lines = pd.DataFrame(all_lines)
    data = all_lines.to_numpy()

    # Convert start, end times to a 2D array
    df_TimeWindow = pd.DataFrame({'start' : start_time_list,
                                'end' : end_time_list})

    # Calculate the mean value at each time point
    # mean_values = all_lines.mean(axis=0, numeric_only=False)
    mean_values = np.nanmean(data, axis=0)
    std_values = np.nanstd(data, axis=0)

    min_length = min(len(mean_values), len(std_values))
    x_data = (np.linspace(0, pre_window_length+post_window_length, min_length)) - pre_window_length

    # Add title and labels to the plot
    plt.title(EVTtype)
    plt.xlabel('Time (sec)')
    plt.ylabel(r'$\Delta$F/F (%)')

    # Add legend
    # plt.legend()
    plt.grid(True)
    plt.xlim(-pre_window_length, post_window_length)
    plt.ylim(-6, 15)
    plt.axvline(x=0, color = "red", linestyle = '--', linewidth = 1)

    p2, = ax2.plot(x_data, mean_values, color='green', label='Mean Value', linewidth=4)
    p3 = ax2.fill_between(x_data, mean_values-std_values, mean_values+std_values, facecolor='green', alpha=0.15)
    p4 = ax2.axvline(x=0, linewidth=3, color='slategray', label='Onset')

    ax2.legend(handles=[p1, p2, p4], bbox_to_anchor=(1.1, 1))

    ax3 = fig2.add_subplot(212)
    cs = ax3.imshow(data, cmap=plt.cm.viridis, aspect='auto',
                    interpolation='none', extent=[-pre_window_length,post_window_length,len(data),0], 
                    vmax=int(signal_dF_F.max()), vmin=int(signal_dF_F.min()))
    ax3.set_ylabel('Epoch Number')
    ax3.set_yticks(np.arange(.5, len(data), 2))
    ax3.set_yticklabels(np.arange(0, len(data), 2))
    fig2.colorbar(cs)
    
    if SavePlots == True:
        plt.savefig(os.path.join(output_folder, f"Plot_Epoch_averaging_{EVTtype}_Mean+individual.png"))

    if SaveData==True:
        all_lines.to_pickle(os.path.join(output_folder, 'Data_Extracted_signal_in_EVT1.pkl'))
        df_TimeWindow.to_pickle(os.path.join(output_folder, 'Data_TimeWindow_for_EVT1.pkl'))

    plt.show()

    ####################################################################################################################
    # 5. Extract the signals for the EVT2 epoch
    ####################################################################################################################
    # 선택한 이벤트
    EVTtype = 'EVT2'
    selected_event = 1.0 # '1' means the onset time of the event.

    # 선택한 이벤트에 해당하는 행 필터링
    selected_events_data = df_EVT[df_EVT[EVTtype] == selected_event].copy() #SettingWithCopyWarning 참고 
    selected_events_data['EVT_time'] = list((selected_events_data.index+1)/FPS)

    # 그래프 생성
    fig3 =plt.figure(figsize=(6, 10))
    ax4 = fig3.add_subplot(211)


    # 각 이벤트에 대해 데이터를 추출하고 lineplot으로 그림
    all_lines2 = [] 

    # start_time과 end_time을 저장할 변수 생성 
    start_time_list = []
    end_time_list = []

    pre_window_length = PRE_TIME
    post_window_length = POST_TIME 

    # 모든 line들을 저장하기 위한 리스트
    for index, row in selected_events_data.iterrows():
        selected_event_time = row['EVT_time']

        # 이벤트 발생 시간을 기준으로 2초 전부터 3초 후까지의 데이터 추출
        start_time = selected_event_time - pre_window_length
        end_time = selected_event_time + post_window_length
        filtered_data = GCaMP_signal[(GCaMP_signal['time'] >= start_time) & (GCaMP_signal['time'] <= end_time)]

        # 시간을 조정하여 데이터 시점을 맞춤
        filtered_data = filtered_data.copy() #SettingWithCopyWarning 참고 
        filtered_data['time'] -= selected_event_time

        # lineplot 그리기 (투명도를 조절하여 녹색으로 표시)
        x_data = filtered_data['time']
        y_data = filtered_data['value']
        
        p1, = ax4.plot(x_data, y_data, color=[.7, .7, .7], linewidth=.5, label='Individual Trials')
        all_lines2.append(y_data.values)  # 각 시점에서의 데이터들을 저장
        start_time_list.append(start_time)
        end_time_list.append(end_time)

    # 모든 시점에서의 데이터들을 2차원 배열로 변환
    all_lines2 = pd.DataFrame(all_lines2)
    data2 = all_lines2.to_numpy()

    # start, end 시간을 2차원 배열로 변환 
    df_TimeWindow = pd.DataFrame({'start' : start_time_list,
                                'end' : end_time_list})

    # 각 시점에서의 데이터들의 평균값 계산
    # mean_values = all_lines.mean(axis=0, numeric_only=False)
    mean_values = np.nanmean(data2, axis=0)
    std_values = np.nanstd(data2, axis=0)

    min_length = min(len(mean_values), len(std_values))
    x_data = (np.linspace(0, pre_window_length+post_window_length, min_length))-pre_window_length

    # 그래프 제목과 레이블 추가
    plt.title(EVTtype)
    plt.xlabel('Time (sec)')
    plt.ylabel(r'$\Delta$F/F (%)')

    # 범례 추가
    # plt.legend()
    plt.grid(True)
    plt.ylim(-6, 15)
    plt.xlim(-pre_window_length, post_window_length)
    plt.axvline(x=0, color = "red", linestyle = '--', linewidth = 1)

    p2, = ax4.plot(x_data, mean_values, color='green', label='Mean Value', linewidth=4)
    p3 = ax4.fill_between(x_data, mean_values-std_values, mean_values+std_values, facecolor='green', alpha=0.15)
    p4 = ax4.axvline(x=0, linewidth=3, color='slategray', label='Onset')

    ax4.legend(handles=[p1, p2, p4], bbox_to_anchor=(1.1, 1))

    ax5 = fig3.add_subplot(212)
    cs = ax5.imshow(data2, cmap=plt.cm.viridis, aspect='auto',
                    interpolation='none', extent=[-pre_window_length,post_window_length,len(data2),0],
                    vmax=int(signal_dF_F.max()), vmin=int(signal_dF_F.min()))
    ax5.set_ylabel('Trial Number')
    ax5.set_yticks(np.arange(.5, len(data2), 2))
    ax5.set_yticklabels(np.arange(0, len(data2), 2))
    fig3.colorbar(cs)
    
    if SavePlots == True:
        plt.savefig(os.path.join(output_folder, f"Plot_Epoch_averaging_{EVTtype}_Mean+individual.png"))

    if SaveData==True:
        all_lines2.to_pickle(os.path.join(output_folder, f'Data_Extracted_signal_in_{EVTtype}.pkl'))
        df_TimeWindow.to_pickle(os.path.join(output_folder, f'Data_TimeWindow_for_{EVTtype}.pkl'))

    plt.show()

    ####################################################################################################################
    # 6. Extract the signals for the EVT3 epoch
    ####################################################################################################################
    # 선택한 이벤트
    EVTtype = 'EVT3'
    selected_event = 1.0 # '1' means the onset time of the event.

    # 선택한 이벤트에 해당하는 행 필터링
    selected_events_data = df_EVT[df_EVT[EVTtype] == selected_event].copy() #SettingWithCopyWarning 참고 
    selected_events_data['EVT_time'] = list((selected_events_data.index+1)/FPS)

    # 그래프 생성
    fig4 =plt.figure(figsize=(6, 10))
    ax6 = fig4.add_subplot(211)

    # 각 이벤트에 대해 데이터를 추출하고 lineplot으로 그림
    all_lines3 = []  

    # start_time과 end_time을 저장할 변수 생성 
    start_time_list = []
    end_time_list = []

    # 이벤트 발생 시간을 기준으로 몇 초 이전의 데이터와 몇 초 이후의 데이터까지 추출할지 결정 
    pre_window_length = PRE_TIME
    post_window_length = POST_TIME

    # 모든 line들을 저장하기 위한 리스트
    for index, row in selected_events_data.iterrows():
        selected_event_time = row['EVT_time']

        # 이벤트 발생 시간을 기준으로 2초 전부터 3초 후까지의 데이터 추출
        start_time = selected_event_time - pre_window_length
        end_time = selected_event_time + post_window_length
        filtered_data = GCaMP_signal[(GCaMP_signal['time'] >= start_time) & (GCaMP_signal['time'] <= end_time)]

        # 시간을 조정하여 데이터 시점을 맞춤
        filtered_data = filtered_data.copy() #SettingWithCopyWarning 참고 
        filtered_data['time'] -= selected_event_time

        # lineplot 그리기 (투명도를 조절하여 녹색으로 표시)
        x_data = filtered_data['time']
        y_data = filtered_data['value']
        
        p1, = ax6.plot(x_data, y_data, color=[.7, .7, .7], linewidth=.5, label='Individual Trials')
        all_lines3.append(y_data.values)  # 각 시점에서의 데이터들을 저장
        start_time_list.append(start_time)
        end_time_list.append(end_time)


    # 모든 시점에서의 데이터들을 2차원 배열로 변환
    all_lines3 = pd.DataFrame(all_lines3)
    data3 = all_lines3.to_numpy()

    # start, end 시간을 2차원 배열로 변환 
    df_TimeWindow = pd.DataFrame({'start' : start_time_list,
                                'end' : end_time_list})

    # 각 시점에서의 데이터들의 평균값 계산
    # mean_values = all_lines.mean(axis=0, numeric_only=False)
    mean_values = np.nanmean(data3, axis=0)
    std_values = np.nanstd(data3, axis=0)

    min_length = min(len(mean_values), len(std_values))
    x_data = (np.linspace(0, pre_window_length+post_window_length, min_length))-pre_window_length

    # 그래프 제목과 레이블 추가
    ax6.set_title(EVTtype)
    ax6.set_xlabel('Time (sec)')
    ax6.set_ylabel(r'$\Delta$F/F (%)')

    # plt.legend() # 범례 추가
    plt.grid(True)
    plt.ylim(-6, 15)
    plt.xlim(-pre_window_length, post_window_length)
    # plt.rc('axes', labelsize=30)
    # plt.rc('xtick', labelsize=20)
    # plt.rc('ytick', labelsize=20)
    p2, = ax6.plot(x_data, mean_values, color='green', label='Mean Value', linewidth=4)
    p3 = ax6.fill_between(x_data, mean_values-std_values, mean_values+std_values, facecolor='green', alpha=0.15)
    p4 = ax6.axvline(x=0, linewidth=3, color='slategray', label='Onset')

    ax6.legend(handles=[p1, p2, p4], bbox_to_anchor=(1.1, 1))

    ax7 = fig4.add_subplot(212)
    cs = ax7.imshow(data3, cmap=plt.cm.viridis, aspect='auto',
                    interpolation='none', extent=[-pre_window_length,post_window_length,len(data3),0],
                    vmax=int(signal_dF_F.max()), vmin=int(signal_dF_F.min()))
    ax7.set_ylabel('Trial Number')
    ax7.set_yticks(np.arange(.5, len(data3), 2))
    ax7.set_yticklabels(np.arange(0, len(data3), 2))
    fig4.colorbar(cs)

    if SavePlots == True:
        plt.savefig(os.path.join(output_folder, f"Plot_Epoch_averaging_{EVTtype}_Mean+individual.png"))

    if SaveData==True:
        all_lines3.to_pickle(os.path.join(output_folder, f'Data_Extracted_signal_in_{EVTtype}.pkl'))
        df_TimeWindow.to_pickle(os.path.join(output_folder, f'Data_TimeWindow_for_{EVTtype}.pkl'))

    plt.show()

    return

########################################################################################################################
########################################################################################################################
########################################################################################################################

def Epoch_Analysis_2EVT(pkl_path:str = "Final_table_raw_trace.pkl",
                evt_path:str = "Data_DLC.csv",
                PRE_TIME:int = 5,
                POST_TIME:int = 10,
                FPS:int = 25,
                Rec_duration:int = 600,
                SavePlots:bool = False,
                SaveData:bool = False,
                output_folder:str = "Epoch_Analysis"):
    '''
    This function performs epoch analysis on the processed fluorescence data, aligning the data to behavioral events and extracting relevant information about these epochs.

    Parameters:
    pkl_path (str): Path to the pickle file containing the processed fluorescence data.
    evt_path (str): Path to the CSV file containing the behavioral events data.
    Pre_window_len (int): Length of the pre-event window in seconds.
    Post_window_len (int): Length of the post-event window in seconds.
    FPS (int): Frames per second of the recording.
    Rec_duration (int): Duration of the recording in seconds.
    SavePlots (bool): Whether to save the plots of the detected epochs.
    SaveData (bool): Whether to save the data of the detected epochs.

    Returns:
    None

    '''

    ####################################################################################################################
    # 1. Import necessary libraries
    ####################################################################################################################
    import os
    import pandas as pd
    import numpy as  np
    import pylab as plt
    from matplotlib.patches import Patch
        
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # os.chdir(output_folder)

    ####################################################################################################################
    # 2. Load the data
    ####################################################################################################################
    GCaMP_signal = pd.read_pickle(pkl_path)
    time_sec = GCaMP_signal.time
    signal_dF_F = GCaMP_signal.value

    df_EVT = pd.read_csv(evt_path, header=0, index_col=0)

    ####################################################################################################################
    # 3. Generate plots of the fluorescence signal aligned to behavioral events
    ####################################################################################################################
    # Generate time series of behavioral data
    CamTickTime = np.linspace(0, Rec_duration, Rec_duration*FPS)

    # First make a continous time series of social events
    # Event1 index == 1이면 Nose-to-Snout interaction ON, Event1 index == 2이면 Nose-to-Snout interaction OFF.
    if 'EVT1' in df_EVT.columns: 
        S_interaction_ON = np.array(CamTickTime[df_EVT.EVT1 == 1])
        S_interaction_OFF = np.array(CamTickTime[df_EVT.EVT1 == 2])

    # If Event2_index == 1, else -> S_zone entry, if EVT2 == 2, S_zone -> else exit.
    S_zone_in = np.array(CamTickTime[df_EVT.EVT2 == 1]) 
    # S_zone_in = np.insert(S_zone_in,0,CamTick[0]) # Adjust the index of Frame0 arbitrarily if starting from S_zone.
    S_zone_out = np.array(CamTickTime[df_EVT.EVT2 == 2]) 

    # Similarly for E-zone. If EVT3 == 1, else -> E-zone, if EVT3 == 2, E-zone -> else
    E_zone_in = np.array(CamTickTime[df_EVT.EVT3 == 1])
    E_zone_out = np.array(CamTickTime[df_EVT.EVT3 == 2])

    # First subplot in a series: dFF with social epocs
    fig1 = plt.figure(figsize=(10,6))
    ax1 = fig1.add_subplot(211)

    # Create the line plot
    p1, = ax1.plot(time_sec, signal_dF_F,linewidth=1, color='green', label='GCaMP')

    # Add the vertical spnas using 'axvspan'.
    for on, off in zip(S_zone_in, S_zone_out):
        ax1.axvspan(on, off, alpha=0.25, color='dodgerblue')
    for on, off in zip(E_zone_in, E_zone_out):
        ax1.axvspan(on, off, alpha=0.25, color='orange')
    ax1.set_ylim(-10, 15)
    ax1.set_xlim(0, 600)
    ax1.set_ylabel(r'$\Delta$F/F (%)')
    ax1.set_xlabel('Time (sec)')
    ax1.set_title('dFF with ROI segmentation')

    # Create a custom legend for the vertical spans. 
    handles, labels = ax1.get_legend_handles_labels()
    handles.append(Patch(color='dodgerblue', alpha=0.25, label='S-zone'))
    handles.append(Patch(color='orange', alpha=0.25, label='E-zone'))

    ax1.legend(handles=handles, loc='lower right',bbox_to_anchor=(1.1, 1))

    fig1.tight_layout()

    if SavePlots == True: 
        fig1.savefig(os.path.join(output_folder, 'Plot_dFF_with_ROI_segmentation.png'))

    plt.show()

    ####################################################################################################################
    # 4. Extract the signals for the EVT1 epoch
    ####################################################################################################################

    ####################################################################################################################
    # 5. Extract the signals for the EVT2 epoch
    ####################################################################################################################
    # 선택한 이벤트
    EVTtype = 'EVT2'
    selected_event = 1.0 # '1' means the onset time of the event.

    # 선택한 이벤트에 해당하는 행 필터링
    selected_events_data = df_EVT[df_EVT[EVTtype] == selected_event].copy() #SettingWithCopyWarning 참고 
    selected_events_data['EVT_time'] = list((selected_events_data.index+1)/FPS)

    # 그래프 생성
    fig3 =plt.figure(figsize=(6, 10))
    ax4 = fig3.add_subplot(211)


    # 각 이벤트에 대해 데이터를 추출하고 lineplot으로 그림
    all_lines2 = [] 

    # start_time과 end_time을 저장할 변수 생성 
    start_time_list = []
    end_time_list = []

    pre_window_length = PRE_TIME
    post_window_length = POST_TIME

    # 모든 line들을 저장하기 위한 리스트
    for index, row in selected_events_data.iterrows():
        selected_event_time = row['EVT_time']

        # 이벤트 발생 시간을 기준으로 2초 전부터 3초 후까지의 데이터 추출
        start_time = selected_event_time - pre_window_length
        end_time = selected_event_time + post_window_length
        filtered_data = GCaMP_signal[(GCaMP_signal['time'] >= start_time) & (GCaMP_signal['time'] <= end_time)]

        # 시간을 조정하여 데이터 시점을 맞춤
        filtered_data = filtered_data.copy() #SettingWithCopyWarning 참고 
        filtered_data['time'] -= selected_event_time

        # lineplot 그리기 (투명도를 조절하여 녹색으로 표시)
        x_data = filtered_data['time']
        y_data = filtered_data['value']
        
        p1, = ax4.plot(x_data, y_data, color=[.7, .7, .7], linewidth=.5, label='Individual Trials')
        all_lines2.append(y_data.values)  # 각 시점에서의 데이터들을 저장
        start_time_list.append(start_time)
        end_time_list.append(end_time)

    # 모든 시점에서의 데이터들을 2차원 배열로 변환
    all_lines2 = pd.DataFrame(all_lines2)
    data2 = all_lines2.to_numpy()

    # start, end 시간을 2차원 배열로 변환 
    df_TimeWindow = pd.DataFrame({'start' : start_time_list,
                                'end' : end_time_list})

    # 각 시점에서의 데이터들의 평균값 계산
    # mean_values = all_lines.mean(axis=0, numeric_only=False)
    mean_values = np.nanmean(data2, axis=0)
    std_values = np.nanstd(data2, axis=0)

    min_length = min(len(mean_values), len(std_values))
    x_data = (np.linspace(0, pre_window_length+post_window_length, min_length))-pre_window_length

    # 그래프 제목과 레이블 추가
    plt.title(EVTtype)
    plt.xlabel('Time (sec)')
    plt.ylabel(r'$\Delta$F/F (%)')

    # 범례 추가
    # plt.legend()
    plt.grid(True)
    plt.ylim(-6, 15)
    plt.xlim(-pre_window_length, post_window_length)
    plt.axvline(x=0, color = "red", linestyle = '--', linewidth = 1)

    p2, = ax4.plot(x_data, mean_values, color='green', label='Mean Value', linewidth=4)
    p3 = ax4.fill_between(x_data, mean_values-std_values, mean_values+std_values, facecolor='green', alpha=0.15)
    p4 = ax4.axvline(x=0, linewidth=3, color='slategray', label='Onset')

    ax4.legend(handles=[p1, p2, p4], bbox_to_anchor=(1.1, 1))

    ax5 = fig3.add_subplot(212)
    cs = ax5.imshow(data2, cmap=plt.cm.viridis, aspect='auto',
                    interpolation='none', extent=[-pre_window_length,post_window_length,len(data2),0],
                    vmax=int(signal_dF_F.max()), vmin=int(signal_dF_F.min()))
    ax5.set_ylabel('Trial Number')
    ax5.set_yticks(np.arange(.5, len(data2), 2))
    ax5.set_yticklabels(np.arange(0, len(data2), 2))
    fig3.colorbar(cs)
    
    if SavePlots == True:
        plt.savefig(os.path.join(output_folder, f"Plot_Epoch_averaging_{EVTtype}_Mean+individual.png"))

    if SaveData==True:
        all_lines2.to_pickle(os.path.join(output_folder, f'Data_Extracted_signal_in_{EVTtype}.pkl'))
        df_TimeWindow.to_pickle(os.path.join(output_folder, f'Data_TimeWindow_for_{EVTtype}.pkl'))

    plt.show()

    ####################################################################################################################
    # 6. Extract the signals for the EVT3 epoch
    ####################################################################################################################
    # 선택한 이벤트
    EVTtype = 'EVT3'
    selected_event = 1.0 # '1' means the onset time of the event.

    # 선택한 이벤트에 해당하는 행 필터링
    selected_events_data = df_EVT[df_EVT[EVTtype] == selected_event].copy() #SettingWithCopyWarning 참고 
    selected_events_data['EVT_time'] = list((selected_events_data.index+1)/FPS)

    # 그래프 생성
    fig4 =plt.figure(figsize=(6, 10))
    ax6 = fig4.add_subplot(211)

    # 각 이벤트에 대해 데이터를 추출하고 lineplot으로 그림
    all_lines3 = []  

    # start_time과 end_time을 저장할 변수 생성 
    start_time_list = []
    end_time_list = []

    # 이벤트 발생 시간을 기준으로 몇 초 이전의 데이터와 몇 초 이후의 데이터까지 추출할지 결정 
    pre_window_length = PRE_TIME
    post_window_length = POST_TIME 

    # 모든 line들을 저장하기 위한 리스트
    for index, row in selected_events_data.iterrows():
        selected_event_time = row['EVT_time']

        # 이벤트 발생 시간을 기준으로 2초 전부터 3초 후까지의 데이터 추출
        start_time = selected_event_time - pre_window_length
        end_time = selected_event_time + post_window_length
        filtered_data = GCaMP_signal[(GCaMP_signal['time'] >= start_time) & (GCaMP_signal['time'] <= end_time)]

        # 시간을 조정하여 데이터 시점을 맞춤
        filtered_data = filtered_data.copy() #SettingWithCopyWarning 참고 
        filtered_data['time'] -= selected_event_time

        # lineplot 그리기 (투명도를 조절하여 녹색으로 표시)
        x_data = filtered_data['time']
        y_data = filtered_data['value']
        
        p1, = ax6.plot(x_data, y_data, color=[.7, .7, .7], linewidth=.5, label='Individual Trials')
        all_lines3.append(y_data.values)  # 각 시점에서의 데이터들을 저장
        start_time_list.append(start_time)
        end_time_list.append(end_time)


    # 모든 시점에서의 데이터들을 2차원 배열로 변환
    all_lines3 = pd.DataFrame(all_lines3)
    data3 = all_lines3.to_numpy()

    # start, end 시간을 2차원 배열로 변환 
    df_TimeWindow = pd.DataFrame({'start' : start_time_list,
                                'end' : end_time_list})

    # 각 시점에서의 데이터들의 평균값 계산
    # mean_values = all_lines.mean(axis=0, numeric_only=False)
    mean_values = np.nanmean(data3, axis=0)
    std_values = np.nanstd(data3, axis=0)

    min_length = min(len(mean_values), len(std_values))
    x_data = (np.linspace(0, pre_window_length+post_window_length, min_length))-pre_window_length

    # 그래프 제목과 레이블 추가
    ax6.set_title(EVTtype)
    ax6.set_xlabel('Time (sec)')
    ax6.set_ylabel(r'$\Delta$F/F (%)')

    # plt.legend() # 범례 추가
    plt.grid(True)
    plt.ylim(-6, 15)
    plt.xlim(-pre_window_length, post_window_length)
    # plt.rc('axes', labelsize=30)
    # plt.rc('xtick', labelsize=20)
    # plt.rc('ytick', labelsize=20)
    p2, = ax6.plot(x_data, mean_values, color='green', label='Mean Value', linewidth=4)
    p3 = ax6.fill_between(x_data, mean_values-std_values, mean_values+std_values, facecolor='green', alpha=0.15)
    p4 = ax6.axvline(x=0, linewidth=3, color='slategray', label='Onset')

    ax6.legend(handles=[p1, p2, p4], bbox_to_anchor=(1.1, 1))

    ax7 = fig4.add_subplot(212)
    cs = ax7.imshow(data3, cmap=plt.cm.viridis, aspect='auto',
                    interpolation='none', extent=[-pre_window_length,post_window_length,len(data3),0],
                    vmax=int(signal_dF_F.max()), vmin=int(signal_dF_F.min()))
    ax7.set_ylabel('Trial Number')
    ax7.set_yticks(np.arange(.5, len(data3), 2))
    ax7.set_yticklabels(np.arange(0, len(data3), 2))
    fig4.colorbar(cs)

    if SavePlots == True:
        plt.savefig(os.path.join(output_folder, f"Plot_Epoch_averaging_{EVTtype}_Mean+individual.png"))

    if SaveData==True:
        all_lines3.to_pickle(os.path.join(output_folder, f'Data_Extracted_signal_in_{EVTtype}.pkl'))
        df_TimeWindow.to_pickle(os.path.join(output_folder, f'Data_TimeWindow_for_{EVTtype}.pkl'))

    plt.show()

    return

########################################################################################################################
########################################################################################################################
########################################################################################################################

def Eport_Epoch_Info(TDT_Tank_path:str, REF_EPOC:str = 'PC1_', Time4Exclude:int = 2, destfolder:str = '', SaveData:bool = False):
    '''
    This function extracts the information about the epochs from the synapse Tank data and save it as a CSV file.
    
    Parameters:
    TDT_Tank_path (str): Path to the folder containing Tank files generated by TDT syanpse.
    REF_EPOC (str): The name of channel that contains the epochs information.
    Time4Exclude (int): Time in seconds to exclude from the start of recored data used the signal preprocessing. 
    SaveData (bool): Whether to save the extracted data as a CSV file.
    
    -------------------------------------------
    Returns:
    df_EPOC (pd.DataFrame): DataFrame containing the extracted epoch information. It has two columns with header: 'onset' and 'offset'. All data is in seconds. 

    Example usage:
    TDT_Tank_path = "path/to/tank/folder"
    REF_EPOC = "PC1_"
    Time4Exclude = 2
    SaveData = True
    df_EPOC = Eport_Epoch_Info(TDT_Tank_path, REF_EPOC, Time4Exclude, SaveData)
    print(df_EPOC)
    '''

    import os
    import numpy as np
    import pandas as pd
    import tdt

    FPdata = tdt.read_block(TDT_Tank_path)
    EPOC = FPdata.epocs[REF_EPOC]
    df_EPOC = pd.DataFrame({'onset': EPOC.onset, 
                            'offset': EPOC.offset})
    df_EPOC = df_EPOC - Time4Exclude
    
    if SaveData:
        if destfolder == '':
            destfolder = TDT_Tank_path
        else:
            if not os.path.exists(destfolder):
                os.makedirs(destfolder)
        df_EPOC.to_csv(os.path.join(destfolder, 'Data_EPOC.csv'), index=False)
    
    print(df_EPOC.head())

    return df_EPOC
    