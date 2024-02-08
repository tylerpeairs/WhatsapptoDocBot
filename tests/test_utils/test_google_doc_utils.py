from pyclbr import Class
import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock
import sys
import difflib
import json
from datetime import datetime
sys.path.append('/Users/tylerpeairs/SoftwareProjects/TestChatbot/python-whatsapp-bot/')
from app.utils.google_doc_utils import create_update_requests, batch_update_google_docs_document, create_google_docs_document, parse_existing_categories, get_google_doc_content

class TestUpdateRequestUtils(unittest.TestCase):

    def test_create_update_requests_existing_category(self):
        doc_content = {
            "content": [
            {
                "endIndex": 1,
                "sectionBreak": {
                "sectionStyle": {
                    "columnSeparatorStyle": "NONE",
                    "contentDirection": "LEFT_TO_RIGHT",
                    "sectionType": "CONTINUOUS"
                }
                }
            },
            {
                "startIndex": 1,
                "endIndex": 19,
                "paragraph": {
                "elements": [
                    {
                    "startIndex": 1,
                    "endIndex": 19,
                    "textRun": {
                        "content": "Existing Category\n",
                        "textStyle": {}
                    }
                    }
                ],
                "paragraphStyle": {
                    "headingId": "h.iizz45crpqxq",
                    "namedStyleType": "HEADING_1",
                    "direction": "LEFT_TO_RIGHT"
                }
                }
            },
            {
                "startIndex": 19,
                "endIndex": 29,
                "paragraph": {
                "elements": [
                    {
                    "startIndex": 19,
                    "endIndex": 29,
                    "textRun": {
                        "content": "Some text\n",
                        "textStyle": {}
                    }
                    }
                ],
                "paragraphStyle": {
                    "namedStyleType": "NORMAL_TEXT",
                    "direction": "LEFT_TO_RIGHT"
                }
                }
            },
            {
                "startIndex": 29,
                "endIndex": 30,
                "paragraph": {
                "elements": [
                    {
                    "startIndex": 29,
                    "endIndex": 30,
                    "textRun": {
                        "content": "\n",
                        "textStyle": {}
                    }
                    }
                ],
                "paragraphStyle": {
                    "headingId": "h.1x1lfuwff1b",
                    "namedStyleType": "HEADING_1",
                    "direction": "LEFT_TO_RIGHT"
                }
                }
            },
            {
                "startIndex": 30,
                "endIndex": 43,
                "paragraph": {
                "elements": [
                    {
                    "startIndex": 30,
                    "endIndex": 43,
                    "textRun": {
                        "content": "New Category\n",
                        "textStyle": {}
                    }
                    }
                ],
                "paragraphStyle": {
                    "headingId": "h.oonnogwpavnu",
                    "namedStyleType": "HEADING_1",
                    "direction": "LEFT_TO_RIGHT"
                }
                }
            },
            {
                "startIndex": 43,
                "endIndex": 53,
                "paragraph": {
                "elements": [
                    {
                    "startIndex": 43,
                    "endIndex": 53,
                    "textRun": {
                        "content": "Some text\n",
                        "textStyle": {}
                    }
                    }
                ],
                "paragraphStyle": {
                    "namedStyleType": "NORMAL_TEXT",
                    "direction": "LEFT_TO_RIGHT"
                }
                }
            },
            {
                "startIndex": 53,
                "endIndex": 54,
                "paragraph": {
                "elements": [
                    {
                    "startIndex": 53,
                    "endIndex": 54,
                    "textRun": {
                        "content": "\n",
                        "textStyle": {}
                    }
                    }
                ],
                "paragraphStyle": {
                    "namedStyleType": "NORMAL_TEXT",
                    "direction": "LEFT_TO_RIGHT"
                }
                }
            }
            ]
        }
        category = 'Existing Category'
        text = 'Some text'

        expected_output =     {
            "requests": [
                {
                "insertText": {
                    "location": {
                    "index": 29
                    },
                    "text": "Some text\n"
                }
                },
                {
                "updateParagraphStyle": {
                    "range": {
                    "startIndex": 29,
                    "endIndex": 39
                    },
                    "paragraphStyle": {
                    "namedStyleType": "NORMAL_TEXT"
                    },
                    "fields": "namedStyleType"
                }
                }
            ]
            }
        
        output = create_update_requests(doc_content, category, text)
        self.assertEqual(output, expected_output, '\n' + '\n'.join(difflib.ndiff(
                    json.dumps(expected_output, indent=2).splitlines(),
                    json.dumps(output, indent=2).splitlines()
                 )))    

    def test_create_update_requests_new_category(self):
        doc_content = {
            "content": [
            {
                "endIndex": 1,
                "sectionBreak": {
                "sectionStyle": {
                    "columnSeparatorStyle": "NONE",
                    "contentDirection": "LEFT_TO_RIGHT",
                    "sectionType": "CONTINUOUS"
                }
                }
            },
            {
                "startIndex": 1,
                "endIndex": 14,
                "paragraph": {
                "elements": [
                    {
                    "startIndex": 1,
                    "endIndex": 14,
                    "textRun": {
                        "content": "Old Category\n",
                        "textStyle": {}
                    }
                    }
                ],
                "paragraphStyle": {
                    "headingId": "h.iizz45crpqxq",
                    "namedStyleType": "HEADING_1",
                    "direction": "LEFT_TO_RIGHT"
                }
                }
            },
            {
                "startIndex": 14,
                "endIndex": 24,
                "paragraph": {
                "elements": [
                    {
                    "startIndex": 14,
                    "endIndex": 24,
                    "textRun": {
                        "content": "Some text\n",
                        "textStyle": {}
                    }
                    }
                ],
                "paragraphStyle": {
                    "namedStyleType": "NORMAL_TEXT",
                    "direction": "LEFT_TO_RIGHT"
                }
                }
            },
            {
                "startIndex": 24,
                "endIndex": 25,
                "paragraph": {
                "elements": [
                    {
                    "startIndex": 24,
                    "endIndex": 25,
                    "textRun": {
                        "content": "\n",
                        "textStyle": {}
                    }
                    }
                ],
                "paragraphStyle": {
                    "namedStyleType": "NORMAL_TEXT",
                    "direction": "LEFT_TO_RIGHT"
                }
                }
            }
            ]
        }

        category = 'New Category'
        text = 'Some text'

        expected_output = {
            "requests": [
                {
                "insertText": {
                    "location": {
                    "index": 24
                    },
                    "text": "\nNew Category\n"
                }
                },
                {
                "updateParagraphStyle": {
                    "range": {
                    "startIndex": 24,
                    "endIndex": 38
                    },
                    "paragraphStyle": {
                    "namedStyleType": "HEADING_1"
                    },
                    "fields": "namedStyleType"
                }
                },
                {
                "insertText": {
                    "location": {
                    "index": 38
                    },
                    "text": "Some text\n"
                }
                },
                {
                "updateParagraphStyle": {
                    "range": {
                    "startIndex": 38,
                    "endIndex": 48
                    },
                    "paragraphStyle": {
                    "namedStyleType": "NORMAL_TEXT"
                    },
                    "fields": "namedStyleType"
                }
                }
            ]
        }
        output = create_update_requests(doc_content, category, text)
        self.assertEqual(output, expected_output, '\n' + '\n'.join(difflib.ndiff(
                    json.dumps(expected_output, indent=2).splitlines(),
                    json.dumps(output, indent=2).splitlines()
                 )))    

    
    def test_create_update_requests_empty_document(self):
        doc_content = {
            "content": [
            {
                "endIndex": 1,
                "sectionBreak": {
                "sectionStyle": {
                    "columnSeparatorStyle": "NONE",
                    "contentDirection": "LEFT_TO_RIGHT",
                    "sectionType": "CONTINUOUS"
                }
                }
            },
            {
                "startIndex": 1,
                "endIndex": 2,
                "paragraph": {
                "elements": [
                    {
                    "startIndex": 1,
                    "endIndex": 2,
                    "textRun": {
                        "content": "\n",
                        "textStyle": {}
                    }
                    }
                ],
                "paragraphStyle": {
                    "namedStyleType": "NORMAL_TEXT",
                    "direction": "LEFT_TO_RIGHT"
                }
                }
            }
            ]
        }
        category = 'New Category'
        text = 'Some text'
        
        expected_output = {
            "requests": [
                {
                "insertText": {
                    "location": {
                    "index": 1
                    },
                    "text": "New Category\n"
                }
                },
                {
                "updateParagraphStyle": {
                    "range": {
                    "startIndex": 1,
                    "endIndex": 14
                    },
                    "paragraphStyle": {
                    "namedStyleType": "HEADING_1"
                    },
                    "fields": "namedStyleType"
                }
                },
                {
                "insertText": {
                    "location": {
                    "index": 14
                    },
                    "text": "Some text\n"
                }
                },
                {
                "updateParagraphStyle": {
                    "range": {
                    "startIndex": 14,
                    "endIndex": 24
                    },
                    "paragraphStyle": {
                    "namedStyleType": "NORMAL_TEXT"
                    },
                    "fields": "namedStyleType"
                }
                }
            ]
        }
        output = create_update_requests(doc_content, category, text)

        self.assertEqual(output, expected_output, '\n' + '\n'.join(difflib.ndiff(
                    json.dumps(expected_output, indent=2).splitlines(),
                    json.dumps(output, indent=2).splitlines()
                 )))    

class TestCreateGoogleDocsDocument(unittest.TestCase):
    @patch('app.utils.google_doc_utils.build')  # Patch the 'build' function
    def test_create_google_docs_document(self, mock_build):
        # Setup the mock for the Google Docs service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock response for the 'create' method
        expected_doc_id = 'abc123'
        mock_service.documents.return_value.create.return_value.execute.return_value = {
            'documentId': expected_doc_id
        }

        # Mock credentials
        mock_credentials = MagicMock()

        # Call the function
        today_date = datetime.now().strftime('%Y-%m-%d')
        expected_document_title = f"Whatsapp Notes {today_date}"
        result = create_google_docs_document(mock_credentials)

        # Assertions
        mock_build.assert_called_once_with('docs', 'v1', credentials=mock_credentials)
        self.assertEqual(result, {'document_id': expected_doc_id, 'document_title': expected_document_title})
        mock_service.documents.return_value.create.assert_called_once_with(body={'title': expected_document_title})


class TestBatchUpdateGoogleDocsDocument(unittest.TestCase): 
    @patch('app.utils.google_doc_utils.build')
    def test_batch_update_google_docs_document(self, mock_build):

        # Setup the mock credentials
        mock_credentials = MagicMock()

        # Mock the Google Docs service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Define the test inputs
        document_id = 'test_document_id'
        update_requests = {
            "requests": [
                {"insertText": {"location": {"index": 1}, "text": "New Category\n"}},
                {"updateParagraphStyle": {"range": {"startIndex": 1, "endIndex": 14}, "paragraphStyle": {"namedStyleType": "HEADING_1"}, "fields": "namedStyleType"}},
                {"insertText": {"location": {"index": 14}, "text": "Some text\n"}},
                {"updateParagraphStyle": {"range": {"startIndex": 14, "endIndex": 24}, "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"}, "fields": "namedStyleType"}}
            ]
        }

        # Define the mocked batchUpdate execute response
        mock_response = {'status': 'success'}
        mock_service.documents().batchUpdate().execute.return_value = mock_response

        # Call the function with the test inputs
        output = batch_update_google_docs_document(mock_credentials, document_id, update_requests)

        # Assert that the function returned the expected output
        self.assertEqual(output, mock_response)

        # Assert that build was called with the correct arguments
        mock_build.assert_called_with('docs', 'v1', credentials=mock_credentials)

        # Assert that batchUpdate().execute() was called with the correct arguments
        mock_service.documents().batchUpdate.assert_called_with(documentId=document_id, body=update_requests)


class TestGetGoogleDocContent(unittest.TestCase):

    @patch('app.utils.google_doc_utils.build')
    def test_get_google_doc_content_success(self, mock_build):
        # Arrange
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.documents().get().execute.return_value = {
            'body': {
                'content': 'test content'
            }
        }
        credentials = 'test credentials'
        document_id = 'test document id'

        # Act
        result = get_google_doc_content(credentials, document_id)

        # Assert
        mock_build.assert_called_once_with('docs', 'v1', credentials=credentials)
        self.assertEqual(result, 'test content')
        mock_service.documents().get.assert_called_with(documentId='test document id')



    @patch('app.utils.google_doc_utils.build')
    def test_get_google_doc_content_failure(self, mock_build):
        # Arrange
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.documents().get().execute.side_effect = Exception('test exception')
        credentials = 'test credentials'
        document_id = 'test document id'

        # Act
        result = get_google_doc_content(credentials, document_id)

        # Assert
        mock_build.assert_called_once_with('docs', 'v1', credentials=credentials)
        mock_service.documents().get.assert_called_with(documentId=document_id)
        self.assertIsNone(result)

class TestParseExistingCategories(unittest.TestCase):

    def test_parse_existing_categories_no_content(self):
        doc_content = {}
        expected_categories = {}
        expected_end_index = 2

        categories, end_index = parse_existing_categories(doc_content)

        self.assertEqual(categories, expected_categories)
        self.assertEqual(end_index, expected_end_index)

    def test_parse_existing_categories_no_paragraphs(self):
        doc_content = {'content': [{'endIndex': 5}]}
        expected_categories = {}
        expected_end_index = 5

        categories, end_index = parse_existing_categories(doc_content)

        self.assertEqual(categories, expected_categories)
        self.assertEqual(end_index, expected_end_index)

    def test_parse_existing_categories_with_categories(self):
        doc_content = {
            'content': [
                {
                    'startIndex': 1,
                    'endIndex': 10,
                    'paragraph': {
                        'paragraphStyle': {'namedStyleType': 'HEADING_1'},
                        'elements': [{'textRun': {'content': 'Category1\n'}}]
                    }
                },
                {
                    'startIndex': 10,
                    'endIndex': 20,
                    'paragraph': {
                        'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'},
                        'elements': [{'textRun': {'content': 'Some text\n'}}]
                    }
                },
                {
                    'startIndex': 20,
                    'endIndex': 30,
                    'paragraph': {
                        'paragraphStyle': {'namedStyleType': 'HEADING_1'},
                        'elements': [{'textRun': {'content': 'Category2\n'}}]
                    }
                },
                {
                    'startIndex': 30,
                    'endIndex': 40,
                    'paragraph': {
                        'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'},
                        'elements': [{'textRun': {'content': 'Some more text\n'}}]
                    }
                },
            ]
        }
        expected_categories = {
            'Category1': {'startIndex': 1, 'endIndex': 20},
            'Category2': {'startIndex': 20, 'endIndex': 40},
        }
        expected_end_index = 40

        categories, end_index = parse_existing_categories(doc_content)

        self.assertEqual(categories, expected_categories)
        self.assertEqual(end_index, expected_end_index)

if __name__ == '__main__':
    unittest.main()