import unittest

from app.models.enums import QuestionType
from app.models.question import Question
from app.services.mocktest.question_evaluator import QuestionEvaluator
from app.services.rag.embeddings.local_hash_embeddings import LocalHashEmbeddings
from app.services.security.check_email import CheckEmail
from app.services.security.password_service import PasswordService


class ServiceUnitTest(unittest.TestCase):
    def test_email_validation(self):
        self.assertTrue(CheckEmail.contains_necessary_character("user@example.com"))
        self.assertFalse(CheckEmail.contains_necessary_character("not-an-email"))

    def test_password_hash_and_strength(self):
        service = PasswordService()
        hashed = service.hash_password("Strong123")
        self.assertTrue(service.verify_password("Strong123", hashed))
        self.assertFalse(service.verify_password("Wrong123", hashed))
        self.assertTrue(service.validate_password_strength("Strong123"))
        self.assertFalse(service.validate_password_strength("weak"))

    def test_question_evaluator_for_mcq_msq_nat(self):
        evaluator = QuestionEvaluator()
        mcq = Question("q1", QuestionType.MCQ, "Pick", "Math", 2, 0.5, "A", ["A", "B"])
        msq = Question("q2", QuestionType.MSQ, "Pick", "Math", 2, 0.5, ["A", "B"], ["A", "B", "C"])
        nat = Question("q3", QuestionType.NAT, "Value", "Math", 2, 0.5, [1.9, 2.1])

        self.assertTrue(evaluator.evaluate(mcq, "A")["correct"])
        self.assertTrue(evaluator.evaluate(msq, ["B", "A"])["correct"])
        self.assertTrue(evaluator.evaluate(nat, "2.0")["correct"])
        self.assertEqual(evaluator.evaluate(mcq, "B")["awarded_marks"], -0.5)

    def test_local_hash_embeddings_are_deterministic(self):
        embeddings = LocalHashEmbeddings(dimensions=16)
        first = embeddings.embed_query("birch clustering")
        second = embeddings.embed_query("birch clustering")
        self.assertEqual(first, second)
        self.assertEqual(len(first), 16)


if __name__ == "__main__":
    unittest.main()
