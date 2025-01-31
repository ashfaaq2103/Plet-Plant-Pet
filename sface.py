import numpy as np
import cv2 as cv

class SFace:
    def __init__(self, modelPath, disType=0, backendId=0, targetId=0):
        """
        Initialize the SFace class.

        Args:
        - modelPath (str): Path to the face recognition model.
        - disType (int): Distance type for matching (0 for cosine similarity, 1 for Norm-L2 distance).
        - backendId (int): Backend identifier for model creation.
        - targetId (int): Target identifier for model creation.
        """
        self._modelPath = modelPath
        self._backendId = backendId
        self._targetId = targetId
        # Create the face recognizer model
        self._model = cv.FaceRecognizerSF.create(
            model=self._modelPath,
            config="",
            backend_id=self._backendId,
            target_id=self._targetId)

        self._disType = disType  # 0: cosine similarity, 1: Norm-L2 distance
        assert self._disType in [0, 1], "0: Cosine similarity, 1: norm-L2 distance, others: invalid"

        # Threshold values for matching
        self._threshold_cosine = 0.363
        self._threshold_norml2 = 1.128

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
        # Recreate the face recognizer model with new backend and target
        self._model = cv.FaceRecognizerSF.create(
            model=self._modelPath,
            config="",
            backend_id=self._backendId,
            target_id=self._targetId)

    def _preprocess(self, image, bbox):
        """
        Preprocess the input image.

        Args:
        - image (numpy.ndarray): Input image.
        - bbox (numpy.ndarray or None): Bounding box of the face region.

        Returns:
        - numpy.ndarray: Preprocessed image.
        """
        if bbox is None:
            return image
        else:
            # Align and crop the face region
            return self._model.alignCrop(image, bbox)

    def infer(self, image, bbox=None):
        """
        Perform inference on the input image.

        Args:
        - image (numpy.ndarray): Input image.
        - bbox (numpy.ndarray or None): Bounding box of the face region.

        Returns:
        - numpy.ndarray: Extracted features from the face region.
        """
        # Preprocess the image
        inputBlob = self._preprocess(image, bbox)

        # Forward pass through the model
        features = self._model.feature(inputBlob)
        return features

    def match(self, image1, face1, image2, face2):
        """
        Match two faces based on their features.

        Args:
        - image1 (numpy.ndarray): First input image.
        - face1 (numpy.ndarray): Features of the first face.
        - image2 (numpy.ndarray): Second input image.
        - face2 (numpy.ndarray): Features of the second face.

        Returns:
        - tuple: A tuple containing the distance/similarity score and the match result (1 for match, 0 for non-match).
        """
        # Extract features for both faces
        feature1 = self.infer(image1, face1)
        feature2 = self.infer(image2, face2)

        if self._disType == 0:  # COSINE
            # Calculate cosine similarity score
            cosine_score = self._model.match(feature1, feature2, self._disType)
            return cosine_score, 1 if cosine_score >= self._threshold_cosine else 0
        else:  # NORM_L2
            # Calculate L2 norm distance
            norml2_distance = self._model.match(feature1, feature2, self._disType)
            return norml2_distance, 1 if norml2_distance <= self._threshold_norml2 else 0
