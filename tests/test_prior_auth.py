import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the 'app' directory and root directory to the python path to allow imports to resolve
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

try:
    from app.utils.processing_file import processing_file
    from app.models.prior_auth_model import get_prior_auth_output_model
except ImportError:
    from utils.processing_file import processing_file
    from models.prior_auth_model import get_prior_auth_output_model

class TestPriorAuth(unittest.TestCase):
    def test_unsupported_extension(self):
        with self.assertRaises(ValueError) as context:
            processing_file("test.txt")
        self.assertIn("Unsupported file format", str(context.exception))

    def test_dynamic_model_generation(self):
        fields = [
            {"name": "last_name", "type": "str", "description": "Last name"},
            {"name": "first_name", "type": "str", "description": "First name"},
            {"name": "date_of_birth", "type": "str", "description": "DOB"},
            {"name": "provider", "type": "str", "description": "Provider"},
            {"name": "NPI", "type": "str", "description": "NPI"},
        ]
        Model = get_prior_auth_output_model(fields)
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

    def test_recursive_dynamic_model_generation(self):
        fields = [
            {
                "name": "patient_name",
                "type": "str",
                "description": "Patient's name",
            },
            {
                "name": "medications",
                "type": "list",
                "description": "List of medications",
                "sub_fields": [
                    {"name": "name", "type": "str", "description": "Name of the drug"},
                    {"name": "dosage", "type": "str", "description": "Dosage"},
                ]
            },
            {
                "name": "allergies",
                "type": "list[str]",
                "description": "List of allergies",
            }
        ]
        Model = get_prior_auth_output_model(fields)
        instance = Model(
            patient_name="Alice",
            medications=[
                {"name": "Aspirin", "dosage": "81mg"},
                {"name": "Lisinopril", "dosage": "10mg"}
            ],
            allergies=["Peanuts", "Penicillin"]
        )
        self.assertEqual(instance.patient_name, "Alice")
        self.assertEqual(len(instance.medications), 2)
        self.assertEqual(instance.medications[0].name, "Aspirin")
        self.assertEqual(instance.medications[0].dosage, "81mg")
        self.assertEqual(instance.medications[1].name, "Lisinopril")
        self.assertEqual(instance.medications[1].dosage, "10mg")
        self.assertEqual(instance.allergies, ["Peanuts", "Penicillin"])

    @patch('app.utils.fille_template_pdf.PdfReader')
    @patch('app.utils.fille_template_pdf.PdfWriter')
    @patch('app.utils.fille_template_pdf.open', create=True)
    def test_fill_template_pdf(self, mock_open, mock_writer_cls, mock_reader_cls):
        # Setup Reader mock
        mock_reader = mock_reader_cls.return_value
        mock_reader.get_fields.return_value = {
            "first_name": "Field info 1",
            "contact_info.name": "Field info 2",
            "medications[0].name": "Field info 3",
            "{{allergies[1]}}": "Field info 4"
        }
        
        # Setup Writer mock
        mock_writer = mock_writer_cls.return_value
        mock_page1 = MagicMock()
        mock_writer.pages = [mock_page1]
        
        # Data to fill
        cv_data = {
            "first_name": "John",
            "contact_info": {
                "name": "John Doe"
            },
            "medications": [
                {"name": "Aspirin"}
            ],
            "allergies": [
                "Peanuts",
                "Penicillin"
            ]
        }
        
        # Call the function
        try:
            from app.utils.fille_template_pdf import fill_template_pdf
        except ImportError:
            from utils.fille_template_pdf import fill_template_pdf
        result = fill_template_pdf("dummy_template.pdf", cv_data, "dummy_output.pdf")
        
        # Assertions
        mock_reader_cls.assert_called_once_with("dummy_template.pdf")
        mock_writer.append.assert_called_once_with(mock_reader)
        
        # Check updates dictionary
        expected_updates = {
            "first_name": "John",
            "contact_info.name": "John Doe",
            "medications[0].name": "Aspirin",
            "{{allergies[1]}}": "Penicillin"
        }
        mock_writer.update_page_form_field_values.assert_called_once_with(mock_page1, expected_updates)
        mock_writer.write.assert_called_once()

    def test_get_conversational_chain_binds_tools(self):
        try:
            from app.chains import chat_chain
        except ImportError:
            from chains import chat_chain

        with patch.object(chat_chain, 'get_llm') as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.bind_tools.return_value = mock_llm
            mock_get_llm.return_value = mock_llm
            
            try:
                from app.chains.chat_chain import get_conversational_chain
            except ImportError:
                from chains.chat_chain import get_conversational_chain

            chain = get_conversational_chain()
            
            # Verify get_llm was called
            mock_get_llm.assert_called_once()
            # Verify bind_tools was called on the mock_llm
            mock_llm.bind_tools.assert_called_once()

    def test_conversational_agent_chain_execution(self):
        try:
            from app.chains.chat_chain import ConversationalAgentChain
        except ImportError:
            from chains.chat_chain import ConversationalAgentChain

        # Mock prompt, LLM and tools
        mock_prompt = MagicMock()
        
        # mock formatted_prompt.to_messages()
        mock_formatted_prompt = MagicMock()
        mock_formatted_prompt.to_messages.return_value = []
        mock_prompt.format_prompt.return_value = mock_formatted_prompt

        # Mock LLM behavior:
        # Iteration 1: return an AIMessage with a tool call
        mock_llm = MagicMock()
        
        from langchain_core.messages import AIMessage
        
        tool_call_dict = {
            "name": "generate_prior_auth",
            "args": {"content": "patient note text"},
            "id": "call_123",
            "type": "tool_call"
        }
        
        mock_response_1 = AIMessage(
            content="",
            tool_calls=[tool_call_dict]
        )
        
        mock_response_2 = AIMessage(
            content="Form generated successfully!",
        )
        
        # side_effect returns mock_response_1 on first call, mock_response_2 on second call
        mock_llm.invoke.side_effect = [mock_response_1, mock_response_2]

        # Mock tool
        mock_tool = MagicMock()
        mock_tool.name = "generate_prior_auth"
        mock_tool.invoke.return_value = "Result path"

        agent = ConversationalAgentChain(
            prompt=mock_prompt,
            llm=mock_llm,
            tools=[mock_tool]
        )

        response = agent.invoke({"input": "Please generate prior auth", "history": []})

        # Assertions
        self.assertEqual(response, "Form generated successfully!")
        self.assertEqual(mock_llm.invoke.call_count, 2)
        mock_tool.invoke.assert_called_once_with({"content": "patient note text"})

if __name__ == "__main__":
    unittest.main()
