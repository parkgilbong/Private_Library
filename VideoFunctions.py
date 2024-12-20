def extract_frames(video_path, frame_indices, output_folder):
    '''extract the specified frames from a video file (*.avi or *.mp4) and save them as PNG images in the output folder.

    Parameters:
    video_path: str. full path of a single video file.
    frame_indices: list of int. Indices of frames that should be extraced from a video file.
    output_folder: str. full path of the folder where the extraced frames will be stored. 

    '''
    import cv2
    import os
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Get the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Ensure frame indices are within the valid range
    frame_indices = [i for i in frame_indices if i < total_frames]

    # Loop through the specified frame indices
    for idx in frame_indices:
        # Set the video position to the specific frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)

        # Read the frame
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Could not read frame {idx}.")
            continue
        
        # Make sure the output folder exists
        if not os.path.exists(output_folder): 
            os.makedirs(output_folder)

        # Save the frame as an image file
        output_path = f"{output_folder}/frame_{idx}.png"
        cv2.imwrite(output_path, frame)
        print(f"Frame {idx} saved as {output_path}")

    # Release the video capture object
    cap.release()

    
    
def extract_video_slices(video_path, slices_df, output_folder):
    '''create individual AVI files for each slice (a pair of the start and end indices) specified in the DataFrame and save them in the output folder.

    Parameters:
    video_path: str. full path of a single video file.
    slices_df: pd.DataFrame. DataFrame containing two columns. Each columns name should be 'start_frame' and 'end_frame'.
    output_folder: str. full path of the folder where the extraced videos will be stored.   

    '''
    import cv2
    import os
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Get the frames per second (fps) of the video
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    slice_number = 1
    for _, row in slices_df.iterrows():
        start_frame = row['start_frame']
        end_frame = row['end_frame']
        
        # Set the video position to the start frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        # Define the codec and create a VideoWriter object to save the sliced video
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        output_path = f"{output_folder}/slice_{slice_number}.avi"
        out = cv2.VideoWriter(output_path, fourcc, fps, 
                              (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                               int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        
        current_frame = start_frame
        while current_frame <= end_frame:
            ret, frame = cap.read()
            if not ret:
                print(f"Error: Could not read frame {current_frame}.")
                break
            
            # Write the frame to the output video
            out.write(frame)
            current_frame += 1

        # Release the VideoWriter object
        out.release()
        slice_number += 1

    # Release the video capture object
    cap.release()
    print("Video slices extraction completed.")



def create_animated_chart(data, filename, interval, offset):
    '''create an animated chart.

    Parameters:
    data: 1D array data to make an animated chart.
    filename: str. the name of the created chart with the extension 'mp4'.
    interval: int. Delay between frames in milliseconds. 
    offset: float.     

    '''
    
    import cv2 
    import numpy as np 
    import matplotlib.pyplot as plt 
    import matplotlib.animation as animation
    
    fig, ax = plt.subplots(figsize=(7.0, 2.5), facecolor='k')
    line, = ax.plot([], [], lw=5, color ='g')
    ax.set_xlim(0-offset, len(data)/interval-offset)
    ax.set_ylim(np.min(data), np.max(data))
    ax.set_xlabel('Time(sec)', fontsize = 12)
    ax.set_ylabel('dF/F (%)', fontsize = 12)
    ax.axvline(x=0, color = 'w', linestyle = ':', linewidth = 2)
    ax.set_facecolor('k')
    ax.xaxis.label.set_color('w')        #setting up X-axis label color to yellow
    ax.yaxis.label.set_color('w')          #setting up Y-axis label color to blue
    ax.tick_params(axis='x', colors='w')    #setting up X-axis tick color to red
    ax.tick_params(axis='y', colors='w')  #setting up Y-axis tick color to black

    def init():
        line.set_data([], [])
        return line,

    def animate(i):
        x = ((np.arange(0, i)/interval)-offset)
        y = data[:i]
        line.set_data(x, y)
        return line,

    ani = animation.FuncAnimation(fig, animate, init_func=init, frames=len(data), interval=100, blit=True)
    ani.save(filename, writer='ffmpeg')



def add_inset_chart(video_slice_path, chart_path, filename, position=('right', 'bottom'), chart_width=480):
    '''add an inset chart to a video file.

    Parameters:
    video_slice_path: 1D array data to make an animated chart.
    chart_path: str. the name of the created chart with the extension 'mp4'.
    filename: int. Delay between frames in milliseconds. 
    position: tuple.
    chart_size: tuple. 

    '''
    from moviepy.editor import VideoFileClip, CompositeVideoClip

    video_clip = VideoFileClip(video_slice_path)
    chart_clip = VideoFileClip(chart_path).resize(width=chart_width)  # Resize chart

    # Determine position
    if position == ('right', 'bottom'):
        pos = (video_clip.w - chart_clip.w, video_clip.h - chart_clip.h)
    elif position == ('right', 'top'):
        pos = (video_clip.w - chart_clip.w, 0)
    elif position == ('left', 'bottom'):
        pos = (0, video_clip.h - chart_clip.h)
    elif position == ('left', 'top'):
        pos = (0, 0)
    else:
        pos = position  # Directly use the provided position if it's a tuple of coordinates

    final_clip = CompositeVideoClip([video_clip, chart_clip.set_position(pos)])
    final_clip.write_videofile(filename, codec='libx264')

