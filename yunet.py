from itertools import product
import numpy as np
import cv2 as cv

class YuNet:
    def __init__(self, modelPath, inputSize=[320, 320], confThreshold=0.6, nmsThreshold=0.3, topK=5000, backendId=0, targetId=0):
        """
        Initialize the YuNet class.

        Args:
        - modelPath (str): Path to the face detection model.
        - inputSize (list): Input size for the model in the format [width, height].
        - confThreshold (float): Confidence threshold for face detection.
        - nmsThreshold (float): Non-maximum suppression threshold.
        - topK (int): Maximum number of detections to keep.
        - backendId (int): Backend identifier for model creation.
        - targetId (int): Target identifier for model creation.
        """
        self._modelPath = modelPath
        self._inputSize = tuple(inputSize)  # [w, h]
        self._confThreshold = confThreshold
        self._nmsThreshold = nmsThreshold
        self._topK = topK
        self._backendId = backendId
        self._targetId = targetId

        # Create the YuNet model for face detection
        self._model = cv.FaceDetectorYN.create(
            model=self._modelPath,
            config="",
            input_size=self._inputSize,
            score_threshold=self._confThreshold,
            nms_threshold=self._nmsThreshold,
            top_k=self._topK,
            backend_id=self._backendId,
            target_id=self._targetId)

    @property
    def name(self):
        """
        Property for getting the class name.
        """
        return self.__class__.__name__

    def setBackendAndTarget(self, backendId, targetId):
        """
        Set the backend and target identifiers.

        Args:
        - backendId (int): Backend identifier.
        - targetId (int): Target identifier.
        """
        self._backendId = backendId
        self._targetId = targetId
        # Recreate the YuNet model with new backend and target
        self._model = cv.FaceDetectorYN.create(
            model=self._modelPath,
            config="",
            input_size=self._inputSize,
            score_threshold=self._confThreshold,
            nms_threshold=self._nmsThreshold,
            top_k=self._topK,
            backend_id=self._backendId,
            target_id=self._targetId)

    def setInputSize(self, input_size):
        """
        Set the input size for the model.

        Args:
        - input_size (list): New input size in the format [width, height].
        """
        self._model.setInputSize(tuple(input_size))

    def infer(self, image):
        """
        Perform inference on the input image.

        Args:
        - image (numpy.ndarray): Input image.

        Returns:
        - numpy.ndarray: Detected faces in the input image.
        """
        # Forward pass through the model to detect faces
        faces = self._model.detect(image)
        # Return empty array if no faces detected, otherwise return the detected faces
        return np.array([]) if faces[1] is None else faces[1]
