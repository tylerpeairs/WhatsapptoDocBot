import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock
import sys
sys.path.append('/Users/tylerpeairs/SoftwareProjects/TestChatbot/python-whatsapp-bot/')
from app.utils.google_doc_utils import create_update_requests, batch_update_google_docs_document

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
        print("Expected Output:", expected_output)
        
        output = create_update_requests(doc_content, category, text)
        print("Output:", output)
        self.assertEqual(output, expected_output) 
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
        print("Expected Output:", expected_output)
        print("Output:", output)
        self.assertEqual(output, expected_output)
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

        self.assertEqual(output, expected_output)


class TestBatchUpdateGoogleDocsDocument(TestCase):
    @patch('app.utils.google_doc_utils.build')
    def test_batch_update_google_docs_document(self, mock_build):
        # Mock the Google Docs service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock the batchUpdate().execute() call
        mock_batch_update = MagicMock()
        mock_service.documents().batchUpdate().execute.return_value = mock_batch_update

        # Define the test inputs
        credentials = 'test_credentials'
        document_id = 'test_document_id'
        update_requests = {
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

        # Define the expected output
        expected_output = mock_batch_update

        # Call the function with the test inputs
        output = batch_update_google_docs_document(credentials, document_id, update_requests)

        # Assert that the function returned the expected output
        self.assertEqual(output, expected_output)

        # Assert that build was called with the correct arguments
        mock_build.assert_called_with('docs', 'v1', credentials=credentials)

        # Assert that batchUpdate().execute() was called with the correct arguments
        mock_service.documents().batchUpdate.assert_called_with(
            documentId=document_id,
            body=update_requests
        )


if __name__ == '__main__':
    unittest.main()