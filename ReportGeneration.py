def FP_preprocessing(output_path:str, title:str, image_paths:list, comments:list):
    """
    Generates a PDF report with the given images, comments, title, date, and time.
    
    Args:
        output_path (str): Path to save the PDF report. .
        image_paths (list of str): List of paths to the images to include in the report.
        comments (list of str): List of comments to add to the report.
        title (str): Title used for the file name and the title of the report.
    
    Example:
        image_paths = ['plot1.png', 'plot2.png', 'plot3.png']
        comments = [
            "This is the first plot showing a simple linear trend.",
            "The second plot shows a slightly different trend.",
            "Here we see the third plot with another set of data."
        ]
        title = "241210 Report"
        output_path = 'C:\\Users\\user\\Document'
        FP_preprocessing(output_path, title, image_paths, comments)
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from datetime import datetime
    from PIL import Image
    import os

    c = canvas.Canvas(os.path.join(output_path, title +'.pdf'), pagesize=letter)
    width, height = letter
    
    # Add title
    title = title 
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, title)
    
    # Add date and time
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Date and Time: {date_time}")
    
    # Add a line separator
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(50, height - 80, width - 50, height - 80)
    
    y_position = height - 100  # Initial y position for the first image
    
    for i, image_path in enumerate(image_paths):
        # Open the image to get its size
        with Image.open(image_path) as img:
            img_width, img_height = img.size
        
        # Calculate the aspect ratio
        aspect_ratio = img_width / img_height
        
        # Define the maximum width and height for the image on the PDF
        max_width = 450
        max_height = 225
        
        # Calculate the dimensions to maintain the aspect ratio
        if aspect_ratio > 1:
            display_width = min(max_width, img_width)
            display_height = display_width / aspect_ratio
        else:
            display_height = min(max_height, img_height)
            display_width = display_height * aspect_ratio
        
        # Add image to the PDF
        c.drawImage(image_path, 50, y_position - display_height, width=display_width, height=display_height)
        
        # Add comments
        comment = comments[i] if i < len(comments) else ""
        c.setFont("Helvetica", 10)
        c.drawString(50, y_position - display_height - 20, comment)
        
        # Update y_position for the next image
        y_position -= (display_height + 50)  # Add some space between images
        
        # Add a new page if necessary
        if y_position < 100:
            c.showPage()
            y_position = height - 100
            # Add title and date/time on new page
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, title)
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, f"Date and Time: {date_time}")
            c.line(50, height - 80, width - 50, height - 80)
    
    c.save()