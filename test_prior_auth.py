import unittest
from app.utils.processing_file import processing_file
from app.models.prior_auth_model import get_prior_auth_output_model
from app.prompts.prior_auth_prompt import FILLABLE_FIELDS

class TestPriorAuth(unittest.TestCase):
    def test_unsupported_extension(self):
        with self.assertRaises(ValueError) as context:
            processing_file("test.txt")
        self.assertIn("Unsupported file format", str(context.exception))

    def test_dynamic_model_generation(self):
        Model = get_prior_auth_output_model(FILLABLE_FIELDS)
        instance = Model(
            last_name="Doe",
            first_name="John",
            date_of_birth="01/01/1990",
            provider="Dr. Smith",
            NPI="1234567890"
        )
        self.assertEqual(instance.last_name, "Doe")
        self.assertEqual(instance.first_name, "John")
        self.assertEqual(instance.date_of_birth, "01/01/1990")
        self.assertEqual(instance.provider, "Dr. Smith")
        self.assertEqual(instance.NPI, "1234567890")

if __name__ == "__main__":
    unittest.main()