from sklearn.neighbors import KNeighborsClassifier
import numpy as np
from .models import Student


# ---------------------------------------------------------------------------
# Language detection & translation
# ---------------------------------------------------------------------------

def translate_to_english(text: str) -> str:
    """
    Detect the language of *text* and translate it to English.
    Returns the original text unchanged if:
      - text is empty / None
      - text is already in English
      - translation fails for any reason (network, quota, etc.)
    """
    if not text or not text.strip():
        return text

    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source='auto', target='en').translate(text.strip())
        # deep-translator returns None on failure; fall back gracefully
        return translated if translated else text
    except Exception:
        # Never crash the main request because of a translation error
        return text


# ---------------------------------------------------------------------------
# KNN model training
# ---------------------------------------------------------------------------

def train_knn_model():
    students = Student.objects.all()
    X = []
    y = []
    for student in students:
        X.append([student.age, student.Medu, student.Fedu, student.traveltime, student.studytime,
                  student.failures, student.famrel, student.freetime, student.goout, student.Dalc, student.Walc,
                  student.health, student.absences, student.G1, student.G2])
        y.append(student.G3)

    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(X, y)

    return knn
