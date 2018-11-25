import numpy as np
import cv2
import base64
from grade_paper import ProcessPage

mx = 0
my = 0

def data_uri_to_cv2_img(uri):
	encoded_data = uri.split(',')[1]
	nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
	img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
	return img

#alogrithm for sorting points clockwise
def clockwise_sort(x):
	global mx
	global my
	return (np.arctan2(x[0] - mx, x[1] - my) + 0.5 * np.pi) % (2*np.pi)

def grading(data_uri):
	global mx 
	global my

	# image = cv2.imread("ljk8.jpg")
	image = data_uri_to_cv2_img(data_uri)
	# cv2.imshow('ah``a', image)
	# cv2.waitKey(0)``
	ratio = len(image[0]) / 500.0 #used for resizing the image
	original_image = image.copy() #make a copy of the original image

	#find contours on the smaller image because it's faster
	image = cv2.resize(image, (0,0), fx=1/ratio, fy=1/ratio)

	#gray and filter the image
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	#bilateral filtering removes noise and preserves edges
	gray = cv2.bilateralFilter(gray, 11, 17, 17)
	#find the edges
	edged = cv2.Canny(gray, 85, 250)
	#find the contours
	temp_img, contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	#sort the contours
	contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

	#find the biggest contour
	biggestContour = None

	# loop over our contours
	for contour in contours:
		# approximate the contour
		peri = cv2.arcLength(contour, True)
		approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

		#return the biggest 4 sided approximated contour
		if len(approx) == 4:
			biggestContour = approx
			break

	#used for the perspective transform
	points = []
	desired_points = [[0,0], [425, 0], [425, 550], [0, 550]] #8.5in by 11in. paper

	#convert to np.float32
	desired_points = np.float32(desired_points)

	#extract points from contour
	if biggestContour is not None:
		for i in range(0, 4):
			points.append(biggestContour[i][0])

	#find midpoint of all the contour points for sorting algorithm
	mx = sum(point[0] for point in points) / 4
	my = sum(point[1] for point in points) / 4

	#sort points
	points.sort(key=clockwise_sort, reverse=True)

	#convert points to np.float32
	points = np.float32(points)

	#resize points so we can take the persepctive transform from the
	#original image giving us the maximum resolution
	paper = []
	points *= ratio
	answers = 1
	if biggestContour is not None:
		#create persepctive matrix
		M = cv2.getPerspectiveTransform(points, desired_points)
		#warp persepctive
		paper = cv2.warpPerspective(original_image, M, (425, 550))
		answers, paper, codes = ProcessPage(paper)
		# cv2.imshow("Scanned Paper", paper)

	#draw the contour
	if biggestContour is not None:
		if answers != -1:
			cv2.drawContours(image, [biggestContour], -1, (0, 255, 0), 3)
			print (answers)
			if codes is not None:
				print (codes)
		else:
			cv2.drawContours(image, [biggestContour], -1, (0, 0, 255), 3)

	# cv2.imshow("Original Image", cv2.resize(image, (0, 0), fx=0.7, fy=0.7))
	# cv2.waitKey(0)

	return codes, answers

# print(grading('asd'))