import cv2
import sys
import math
import argparse
import csv

def draw_rectangle(frame, box, color):
    p1 = (int(box[0]), int(box[1]))
    p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
    cv2.rectangle(frame, p1, p2, color, 2, 1)

def calc_angle(box1, box2):
    x1 = int(box1[0] + box1[2]/2)
    x2 = int(box2[0] + box2[2]/2)
    y1 = int(box1[1] + box1[3]/2)
    y2 = int(box2[1] + box2[3]/2)
    angle = math.atan2(y2 - y1, x2 - x1) * 180 / math.pi
    return angle
        
if __name__ == '__main__' :

    # code for parsing arguments from command line
    # if you don't want to run the code from the command line, comment this out and set the variables directly
    # argparser = argparse.ArgumentParser()
    # argparser.add_argument("--oars", help="the number of oars (REQUIRED)")
    # argparser.add_argument("--videoPathIn", help="path to input video (REQUIRED)")
    # argparser.add_argument("--videoPathOut", help="path to output video, file format should be .avi (optional)")
    # argparser.add_argument("--csvPathOut", help = "path to output csv file with angles (optional)")
    # args = argparser.parse_args()
    # print(args)

    # set variables directly here
    video_filepath_in = "rowingfromabove.mp4"
    video_filepath_out = "tracking.avi"
    csv_filepath_out = "angles.csv" 
    num_oars = int(4)
  
    if video_filepath_in is None:
       #argparser.print_help()
       sys.exit()

    if num_oars is None:
       #argparser.print_help()
       sys.exit()

    if csv_filepath_out is not None:
        fields = ["Frame", "Time"]
        for i in range(num_oars):
            fields.append("Oar " + str(i) + " Angle")
            csv_file = open(csv_filepath_out, 'w')
        csv_writer = csv.writer(csv_file)  
        csv_writer.writerow(fields)

    # Read video
    video = cv2.VideoCapture(video_filepath_in)

    # Exit if video not opened.
    if not video.isOpened():
        print ("Could not open video")
        sys.exit()

    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print ('Cannot read video file')
        sys.exit()
    video_resolution = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    if video_filepath_out is not None:
        video_out = cv2.VideoWriter(video_filepath_out, cv2.VideoWriter_fourcc('M','J','P','G'), video.get(cv2.CAP_PROP_FPS), video_resolution)

    print("Select a starting frame where all oars are clearly in view and NOT underwater.")
    print("Press SPACE to select the current frame and any other key to continue to the next frame")

    while cv2.waitKey(0) != ord(' ') and video.isOpened():

        ok, frame = video.read()
        cv2.imshow('Starting Frame', frame)

        if video_out is not None:
            video_out.write(frame)

    cv2.destroyAllWindows()

    blade_trackers = []
    blade_bboxes = []
    oarlock_trackers = [] 
    oarlock_bboxes = []

    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (191, 255, 0), (255, 165, 0), (255, 215, 0)]

    for i in range(num_oars):
         print("Select the bounding box of the blade of an oar")
         blade_bbox = cv2.selectROI(frame, False)
         blade_bboxes.append(blade_bbox)
         draw_rectangle(frame, blade_bbox, colors[i])

         print("Select the bounding box of the oar lock")
         oarlock_bbox = cv2.selectROI(frame, False)
         oarlock_bboxes.append(oarlock_bbox)
         draw_rectangle(frame, oarlock_bbox, colors[i])

         blade_trackers.append(cv2.TrackerCSRT_create())
         oarlock_trackers.append(cv2.TrackerCSRT_create())

         blade_trackers[i].init(frame, blade_bbox)
         oarlock_trackers[i].init(frame, oarlock_bbox)

    cv2.destroyAllWindows()

    while video.isOpened():
      
        # Read a new frame
        video_reading_success, frame = video.read()

        if not video_reading_success:
            break

        image_text_y_coord = 20
        image_text_y_coord_increment = 30
        
        angles = []

        for i in range(num_oars):

            # Update tracker
            tracking_success_blade, blade_bboxes[i] = blade_trackers[i].update(frame)
            tracking_success_oarlock, oarlock_bboxes[i] = oarlock_trackers[i].update(frame)

            # Draw bounding box and calculate angles
            if tracking_success_blade and tracking_success_oarlock:
                draw_rectangle(frame, blade_bboxes[i], colors[i])
                draw_rectangle(frame, oarlock_bboxes[i], colors[i])
                angle = calc_angle(blade_bboxes[i], oarlock_bboxes[i])
                angles.append(angle)
                cv2.putText(frame, 'Oar ' + str(i) + ' Angle: ' + str(angle), (0, image_text_y_coord), cv2.FONT_HERSHEY_SIMPLEX, 0.75,colors[i],2)
                image_text_y_coord = image_text_y_coord + image_text_y_coord_increment
            else :
                # Tracking failure
                cv2.putText(frame, "Tracking failure detected", (0, image_text_y_coord), cv2.FONT_HERSHEY_SIMPLEX, 0.75, colors[i], 2)
                image_text_y_coord = image_text_y_coord + image_text_y_coord_increment

        # Display result
        cv2.imshow("Tracking", frame)

        if video_out is not None:
            video_out.write(frame)

        if csv_writer is not None:
            current_frame = video.get(cv2.CAP_PROP_POS_FRAMES) + 1
            timestamp = video.get(cv2.CAP_PROP_POS_MSEC) / 1000
            row_data = [current_frame, timestamp]
            row_data.extend(angles)
            csv_writer.writerow(row_data)

        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27 : break

    video_out.release()