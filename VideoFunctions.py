def extract_frames(video_path: str, frame_indices: list, output_folder: str):
    """
    Extract the specified frames from a video file (*.avi or *.mp4) and save them as PNG images in the output folder.

    Parameters:
    - video_path (str): Full path of a single video file. This should be a valid path to a video file in .avi or .mp4 format.
    - frame_indices (list of int): Indices of frames that should be extracted from the video file. These should be valid frame indices within the range of the video.
    - output_folder (str): Full path of the folder where the extracted frames will be stored. This should be a valid directory path.

    Returns:
    - None

    Example:
        video_path = 'C:/Users/YGKim_IBS/Videos/sample.mp4'
        frame_indices = [10, 20, 30]
        output_folder = 'C:/Users/YGKim_IBS/ExtractedFrames'
        extract_frames(video_path, frame_indices, output_folder)
        =========================================================================
        This will extract frames 10, 20, and 30 from the specified video and save them as PNG images in the output folder.

    Notes:
    - The function uses OpenCV to read and process the video file.
    - If the specified frame indices are out of range, they will be ignored.
    - The function prints messages indicating the status of frame extraction and any errors encountered.
    """
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

######################################################################################################################################################################    
######################################################################################################################################################################

def extract_video_slices(video_path: str, slices_df, output_folder: str):
    """
    Create individual AVI files for each slice (a pair of the start and end indices) specified in the DataFrame and save them in the output folder.

    Parameters:
    - video_path (str): Full path of a single video file. This should be a valid path to a video file in .avi or .mp4 format.
    - slices_df (pd.DataFrame): DataFrame containing two columns named 'start_frame' and 'end_frame'. Each row specifies a slice of the video to be extracted.
    - output_folder (str): Full path of the folder where the extracted videos will be stored. This should be a valid directory path.

    Returns:
    - None

    Example:
        video_path = 'C:/Users/YGKim_IBS/Videos/sample.mp4'
        slices_df = pd.DataFrame({'start_frame': [10, 50], 'end_frame': [20, 60]})
        output_folder = 'C:/Users/YGKim_IBS/ExtractedSlices'
        extract_video_slices(video_path, slices_df, output_folder)
        =========================================================================
        This will create two video slices from the specified video: one from frame 10 to 20 and another from frame 50 to 60, and save them as individual AVI files in the output folder.

    Notes:
    - The function uses OpenCV to read and process the video file.
    - The function prints messages indicating the status of video slice extraction and any errors encountered.
    """
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
        output_path = f"{output_folder}/slice_{slice_number:03d}.avi"
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

######################################################################################################################################################################    
######################################################################################################################################################################

def create_animated_chart(data: list, filename: str, interval: int, offset: float):
    """
    Create an animated chart from the given data and save it as an MP4 file.

    Parameters:
    - data (list of float): 1D array of data to make an animated chart.
    - filename (str): The name of the created chart file with the extension 'mp4'.
    - interval (int): Delay between frames in milliseconds.
    - offset (float): Offset value for the x-axis.

    Returns:
    - None

    Example:
        data = [0.1, 0.2, 0.3, 0.4, 0.5]
        filename = 'animated_chart.mp4'
        interval = 100
        offset = 0.5
        create_animated_chart(data, filename, interval, offset)
        =========================================================================
        This will create an animated chart from the given data and save it as 'animated_chart.mp4'.

    Notes:
    - The function uses Matplotlib to create and animate the chart.
    - The function prints messages indicating the status of chart creation and any errors encountered.
    """
    
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
    print(f"Animated chart saved as {filename}")

######################################################################################################################################################################    
######################################################################################################################################################################

def add_inset_chart(video_slice_path: str, chart_path: str, filename: str, position: tuple = ('right', 'bottom'), chart_width: int = 480):
    """
    Add an inset chart to a video file.

    Parameters:
    - video_slice_path (str): Path to the video slice file.
    - chart_path (str): Path to the chart file (MP4) to be added as an inset.
    - filename (str): The name of the output video file with the inset chart.
    - position (tuple of str): Position of the inset chart in the video. Default is ('right', 'bottom').
    - chart_width (int): Width of the inset chart in pixels. Default is 480.

    Returns:
    - None

    Example:
        video_slice_path = 'video_slice.avi'
        chart_path = 'chart.mp4'
        filename = 'output_with_inset.mp4'
        position = ('right', 'bottom')
        chart_width = 480
        add_inset_chart(video_slice_path, chart_path, filename, position, chart_width)
        =========================================================================
        This will add the chart from 'chart.mp4' as an inset to 'video_slice.avi' and save the result as 'output_with_inset.mp4'.

    Notes:
    - The function uses OpenCV to read and process the video files.
    - The function prints messages indicating the status of the inset chart addition and any errors encountered.
    """

    import cv2
        
    # Open the main video file
    main_cap = cv2.VideoCapture(video_slice_path)
    if not main_cap.isOpened():
        print("Error: Could not open main video.")
        return

    # Open the chart video file
    chart_cap = cv2.VideoCapture(chart_path)
    if not chart_cap.isOpened():
        print("Error: Could not open chart video.")
        return
    
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

######################################################################################################################################################################    
######################################################################################################################################################################

def add_inset_char2(video_slice_path: str, chart_path: str, filename: str, position: tuple = ('right', 'bottom'), chart_width: int = 480):
    """
    Add an inset chart to a video file.

    Parameters:
        - video_slice_path (str): Path to the video slice file.
        - chart_path (str): Path to the chart file (MP4) to be added as an inset.
        - filename (str): The name of the output video file with the inset chart.
        - position (tuple of str): Position of the inset chart in the video. Default is ('right', 'bottom').
        - chart_width (int): Width of the inset chart in pixels. Default is 480.

    Returns:
        - None

    Example:
        video_slice_path = 'video_slice.avi'
        chart_path = 'chart.mp4'
        filename = 'output_with_inset.mp4'
        position = ('right', 'bottom')
        chart_width = 480
        add_inset_chart(video_slice_path, chart_path, filename, position, chart_width)
        =========================================================================
        This will add the chart from 'chart.mp4' as an inset to 'video_slice.avi' and save the result as 'output_with_inset.mp4'.

    Notes:
    - The function uses OpenCV to read and process the video files.
    - The function prints messages indicating the status of the inset chart addition and any errors encountered.
    """
    import cv2
    import numpy as np

    # Open the main video file
    main_cap = cv2.VideoCapture(video_slice_path)
    if not main_cap.isOpened():
        print("Error: Could not open main video.")
        return

    # Open the chart video file
    chart_cap = cv2.VideoCapture(chart_path)
    if not chart_cap.isOpened():
        print("Error: Could not open chart video.")
        return

    # Get properties of the main video
    main_fps = main_cap.get(cv2.CAP_PROP_FPS)
    main_width = int(main_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    main_height = int(main_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calculate the height of the inset chart while maintaining the aspect ratio
    chart_height = int(chart_width * (chart_cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / chart_cap.get(cv2.CAP_PROP_FRAME_WIDTH)))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, main_fps, (main_width, main_height))

    while cap.isOpened():
        ret_main, frame_main = main_cap.read()
        ret_chart, frame_chart = chart_cap.read()

        if not ret_main or not ret_chart:
            break

        # Resize the chart frame
        frame_chart = cv2.resize(frame_chart, (chart_width, chart_height))

        # Determine the position of the inset chart
        if position == ('right', 'bottom'):
            x_offset = main_width - chart_width
            y_offset = main_height - chart_height
        elif position == ('right', 'top'):
            x_offset = main_width - chart_width
            y_offset = 0
        elif position == ('left', 'bottom'):
            x_offset = 0
            y_offset = main_height - chart_height
        elif position == ('left', 'top'):
            x_offset = 0
            y_offset = 0
        else:
            raise ValueError("Invalid position argument. Use ('right', 'bottom'), ('right', 'top'), ('left', 'bottom'), or ('left', 'top').")

        # Add the chart frame to the main frame
        frame_main[y_offset:y_offset + chart_height, x_offset:x_offset + chart_width] = frame_chart

        # Write the frame to the output video
        out.write(frame_main)

    # Release all resources
    main_cap.release()
    chart_cap.release()
    out.release()
    print(f"Video with inset chart saved as {filename}")

######################################################################################################################################################################
######################################################################################################################################################################
def VideoChopper(input_file: str, tags: list = [], chunk_duration: int = 60, startingIdx: int = 0):
    
    """
    Splits the input video into chunks of given duration.
    
    Args:
        input_file (str): Path to the input video file.
        tags (list of str): Tags to add to the chunk file names (e.g., ["3CT", "100lx"]).
        chunk_duration (int): Duration of each chunk in seconds (default: 60).
        startingIdx (int): Starting index for chunk file naming (default: 0).
    
    Example:
        VideoChopper("input.mp4", ["tag1", "tag2"], 60, 0)
        This will split "input.mp4" into 60-second chunks with names like "tag1_tag2_000.mp4", "tag1_tag2_001.mp4", etc.
    """
    
    import cv2
    import os

    # Set the directory to save the video chunks
    current_dir = os.getcwd()
    relative_path = "" #"training_videos"
    absolute_path = os.path.join(current_dir, relative_path)

    # Get the file extension
    _, extension = os.path.splitext (input_file) 
    
    # Open the input video
    video = cv2.VideoCapture(input_file)
    
    if not video.isOpened():
        print(f"Error: Could not open video {input_file}")
        return
    
    # Get video properties
    fps = int(video.get(cv2.CAP_PROP_FPS))
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps  # Total duration of the video in seconds

    print(f"Video loaded: {input_file}")
    print(f"Total Duration: {duration:.2f}s, FPS: {fps}, Resolution: {frame_width}x{frame_height}")
   
    chunk_frames = chunk_duration * fps # Convert chunk duration to frames

    # Initialize indexing variables
    frame_idx = 0
    chunk_idx = 0
    file_idx = startingIdx

    # Process and save video chunks
    while True:
        ret, frame = video.read()
        if not ret:  # End of video
            break

        # Open a new video writer for each chunk
        if frame_idx % chunk_frames == 0:
            if frame_idx > 0:  # Release the previous writer
                writer.release()
                
            if extension == ".avi":
                fourcc = cv2.VideoWriter_fourcc(*'XVID') # Codec for avi format
            elif extension == ".mp4":
                fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec for mp4 format
            else:
                print("unknown filetype; codec error")
                
            # 태그들 이어붙이기
            chunk_file_name = "_".join(tags) + "_" + str(file_idx).zfill(3) + extension

            chunk_file = os.path.join(absolute_path, chunk_file_name)
            
            writer = cv2.VideoWriter(chunk_file, fourcc, fps, (frame_width, frame_height))
            
            chunk_idx += 1
            file_idx += 1

            print(f"Started new chunk: {chunk_file}")

        # Write the current frame to the current chunk
        writer.write(frame)
        frame_idx += 1
        

    # Release resources
    writer.release()
    video.release()
    print("Video chopping completed!")

######################################################################################################################################################################
######################################################################################################################################################################

def create_video_from_images(image_folder:str, output_filename:str, frame_rate:int = 25, duration:int = 600, codec:str = 'mp4v', quality=95):
    """
    Creates a video from a sequence of images in a specified folder.
    Args:
        image_folder (str): Path to the folder containing the images.
        output_filename (str): Name of the output video file.
        frame_rate (int, optional): Frame rate of the video. Defaults to 25.
        duration (int, optional): Duration of the video in seconds. Defaults to 600.
        codec (str, optional): Codec to be used for the video. Defaults to 'mp4v'.
        quality (int, optional): Quality of the video. Defaults to 95.
    Returns:
        None
    Example:
        create_video_from_images('/path/to/images', 'output_video.mp4', frame_rate=30, duration=120, codec='XVID', quality=90)
    """
    
    import cv2
    import os
    
    image_files = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(".jpg") or img.endswith(".png") or img.endswith(".tiff")])
    
    if not image_files:
        print("이미지 파일을 찾을 수 없습니다.")
        return
    
    # 첫 번째 이미지에서 비디오의 크기 설정
    first_image = cv2.imread(image_files[0])
    height, width, layers = first_image.shape

    # 비디오 라이터 객체 생성
    fourcc = cv2.VideoWriter_fourcc(*codec)
    video_writer = cv2.VideoWriter(output_filename, fourcc, frame_rate, (width, height))

    max_index = frame_rate*duration

    for i in range(0, max_index):
        image = cv2.imread(image_files[i])
        video_writer.write(image)

    video_writer.release()
    print(f'비디오 파일이 생성되었습니다: {output_filename}')

######################################################################################################################################################################
######################################################################################################################################################################
def resize_video(input_path, output_path, scale_factor=0.5):
    """
    Resizes a video by a given scale factor and saves the resized video to the specified output path.
    Parameters:
    input_path (str): The path to the input video file.
    output_path (str): The path where the resized video will be saved.
    scale_factor (float, optional): The factor by which to scale the video dimensions. Default is 0.5.
    Returns:
    None
    Example:
    resize_video('input.mp4', 'output.mp4', scale_factor=0.75)
    """
    import cv2
    import os

    # Open the input video
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {input_path}")
        return

    # Get the original width and height of the video
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calculate the new width and height while maintaining the aspect ratio
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (new_width, new_height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize the frame
        resized_frame = cv2.resize(frame, (new_width, new_height))

        # Write the resized frame to the output video
        out.write(resized_frame)

    # Release everything if job is finished
    cap.release()
    out.release()
    print(f"Resized video saved as {output_path}") 

######################################################################################################################################################################
######################################################################################################################################################################
def Generate_montage(input_folder: str, output_filename: str, rows: int = 3, cols: int = 3, frame_rate: int = 25, duration: int = 600, codec: str = 'mp4v', titles: list = [], popups: list = [], scale_factor: float = 1.0):
    """
    Generates a montage movie from movies in a specified folder.
    Args:
        input_folder (str): Path to the folder containing the movies.
        output_filename (str): Name of the output video file.
        rows (int, optional): Number of rows in the montage. Defaults to 3.
        cols (int, optional): Number of columns in the montage. Defaults to 3.
        frame_rate (int, optional): Frame rate of the video. Defaults to 25.
        duration (int, optional): Duration of the video in seconds. Defaults to 600.
        codec (str, optional): Codec to be used for the video. Defaults to 'mp4v'.
        titles (list of str, optional): Titles for each subset movie. Defaults to [].
        popups (list of tuples, optional): Pop-up texts with their start times and durations. Defaults to [].
        scale_factor (float, optional): Scale factor for resizing the montage. Defaults to 1.0.
    Returns:
        None
    Example:
        Generate_montage('/path/to/movies', 'output_montage.mp4', rows=2, cols=2, frame_rate=30, duration=120, codec='XVID', titles=['Title1', 'Title2'], popups=[('Text', 10, 5)], scale_factor=0.5)
    """
    import cv2
    import os
    import numpy as np
    from tqdm import tqdm

    # Get list of movie files in the input folder
    movie_files = [os.path.join(input_folder, movie) for movie in os.listdir(input_folder) if movie.endswith(".mp4") or movie.endswith(".avi")]
    
    if not movie_files:
        print("No movie files found.")
        return
    
    # Open all movie files
    caps = [cv2.VideoCapture(movie) for movie in movie_files]
    if not all(cap.isOpened() for cap in caps):
        print("Error: Could not open one or more movies.")
        return

    # Get the dimensions of the movies
    frame_width = int(caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create a blank canvas for the montage
    montage_height = int(rows * frame_height * scale_factor)
    montage_width = int(cols * frame_width * scale_factor)
    montage = np.zeros((montage_height, montage_width, 3), dtype=np.uint8)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*codec)
    video_writer = cv2.VideoWriter(output_filename, fourcc, frame_rate, (montage_width, montage_height))

    max_index = int(min([cap.get(cv2.CAP_PROP_FRAME_COUNT) for cap in caps]) * (frame_rate / caps[0].get(cv2.CAP_PROP_FPS)))

    for i in tqdm(range(max_index), desc="Generating Montage"):
        # Fill the montage with frames from movies
        for r in range(rows):
            for c in range(cols):
                idx = (i + r * cols + c) % len(caps)  # Loop through the movies
                ret, frame = caps[idx].read()
                if not ret:
                    # If the movie ends, loop it
                    caps[idx].set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = caps[idx].read()
                if ret:
                    # Resize the frame
                    frame = cv2.resize(frame, (int(frame_width * scale_factor), int(frame_height * scale_factor)))
                    # Place the frame in the correct position in the montage
                    montage[r * int(frame_height * scale_factor):(r + 1) * int(frame_height * scale_factor), c * int(frame_width * scale_factor):(c + 1) * int(frame_width * scale_factor)] = frame
                else:
                    # Fill the remaining grid with black if no frame is available
                    montage[r * int(frame_height * scale_factor):(r + 1) * int(frame_height * scale_factor), c * int(frame_width * scale_factor):(c + 1) * int(frame_width * scale_factor)] = np.zeros((int(frame_height * scale_factor), int(frame_width * scale_factor), 3), dtype=np.uint8)

                # Add title to each subset movie
                if titles and idx < len(titles):
                    title = titles[idx % len(titles)]
                    cv2.putText(montage, title, (c * int(frame_width * scale_factor) + 10, r * int(frame_height * scale_factor) + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Add pop-up text
        for text, start_time, duration in popups:
            start_frame = start_time * frame_rate
            end_frame = start_frame + duration * frame_rate
            if start_frame <= i < end_frame:
                cv2.putText(montage, text, (10, montage_height - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Write the montage frame to the video
        video_writer.write(montage)

    video_writer.release()
    for cap in caps:
        cap.release()
    print(f"Montage video saved as {output_filename}")