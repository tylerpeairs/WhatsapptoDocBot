import unittest
from unittest import TestCase
from unittest.mock import patch, MagicMock
import difflib
import json
from datetime import datetime
from app.utils.google_doc_utils import create_update_requests, batch_update_google_docs_document, create_google_docs_document, parse_existing_categories, get_google_doc_content

class TestUpdateRequestUtils(unittest.TestCase):

    def test_create_update_requests_existing_category(self):
        doc_content = [
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

    def test_create_update_requests_new_category_trailing_newline(self):
        doc_content = [
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
            "endIndex": 18,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 1,
                  "endIndex": 18,
                  "textRun": {
                    "content": "Debt Obligations\n",
                    "textStyle": {}
                  }
                }
              ],
              "paragraphStyle": {
                "headingId": "h.1wx06ntcwsy",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
              }
            }
          },
          {
            "startIndex": 18,
            "endIndex": 48,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 18,
                  "endIndex": 48,
                  "textRun": {
                    "content": "Owe 6000 pesos to ClimaVista.\n",
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
            "startIndex": 48,
            "endIndex": 92,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 48,
                  "endIndex": 92,
                  "textRun": {
                    "content": "Owe an additional 8000 pesos to ClimaVista.\n",
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
            "startIndex": 92,
            "endIndex": 138,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 92,
                  "endIndex": 138,
                  "textRun": {
                    "content": "Owe an additional 10,000 pesos to ClimaVista.\n",
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
            "startIndex": 138,
            "endIndex": 139,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 138,
                  "endIndex": 139,
                  "textRun": {
                    "content": "\n",
                    "textStyle": {}
                  }
                }
              ],
              "paragraphStyle": {
                "headingId": "h.m5qp55wcfbml",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
              }
            }
          },
          {
            "startIndex": 139,
            "endIndex": 157,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 139,
                  "endIndex": 157,
                  "textRun": {
                    "content": "Programming Tasks\n",
                    "textStyle": {}
                  }
                }
              ],
              "paragraphStyle": {
                "headingId": "h.s8mp9xazjbek",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
              }
            }
          },
          {
            "startIndex": 157,
            "endIndex": 188,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 157,
                  "endIndex": 188,
                  "textRun": {
                    "content": "I need to write some programs.\n",
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
            "startIndex": 188,
            "endIndex": 189,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 188,
                  "endIndex": 189,
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

        category = 'Real Estate Inquiries'
        text = 'Message Oscar regarding some real estate inquiries.'

        expected_output = {
          "requests": [
            {
              "insertText": {
                "location": {
                  "index": 188
                },
                "text": "\n"
              }
            },
            {
              "updateParagraphStyle": {
                "range": {
                  "startIndex": 188,
                  "endIndex": 189
                },
                "paragraphStyle": {
                  "namedStyleType": "NORMAL_TEXT"
                },
                "fields": "namedStyleType"
              }
            },
            {
              "insertText": {
                "location": {
                  "index": 189
                },
                "text": "Real Estate Inquiries\n"
              }
            },
            {
              "updateParagraphStyle": {
                "range": {
                  "startIndex": 189,
                  "endIndex": 212
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
                  "index": 211
                },
                "text": "Message Oscar regarding some real estate inquiries.\n"
              }
            },
            {
              "updateParagraphStyle": {
                "range": {
                  "startIndex": 211,
                  "endIndex": 264
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
        doc_content = [
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

    def test_create_update_requests_existing_category_end_of_document_trailing_newline(self):
        doc_content = [{'endIndex': 1, 'sectionBreak': {'sectionStyle': {'columnSeparatorStyle': 'NONE', 'contentDirection': 'LEFT_TO_RIGHT', 'sectionType': 'CONTINUOUS'}}}, {'startIndex': 1, 'endIndex': 24, 'paragraph': {'elements': [{'startIndex': 1, 'endIndex': 24, 'textRun': {'content': 'Financial Transactions\n', 'textStyle': {}}}], 'paragraphStyle': {'headingId': 'h.j8f7cok0s5ox', 'namedStyleType': 'HEADING_1', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 24, 'endIndex': 54, 'paragraph': {'elements': [{'startIndex': 24, 'endIndex': 54, 'textRun': {'content': 'Please give Austin 300 pesos.\n', 'textStyle': {}}}], 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 54, 'endIndex': 87, 'paragraph': {'elements': [{'startIndex': 54, 'endIndex': 87, 'textRun': {'content': 'Please transfer 500 pesos to Ty.\n', 'textStyle': {}}}], 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 87, 'endIndex': 88, 'paragraph': {'elements': [{'startIndex': 87, 'endIndex': 88, 'textRun': {'content': '\n', 'textStyle': {}}}], 'paragraphStyle': {'headingId': 'h.ymjyujutzmie', 'namedStyleType': 'HEADING_1', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 88, 'endIndex': 101, 'paragraph': {'elements': [{'startIndex': 88, 'endIndex': 101, 'textRun': {'content': 'Social Plans\n', 'textStyle': {}}}], 'paragraphStyle': {'headingId': 'h.ili04vc9w7k3', 'namedStyleType': 'HEADING_1', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 101, 'endIndex': 145, 'paragraph': {'elements': [{'startIndex': 101, 'endIndex': 145, 'textRun': {'content': 'Are we making any dinner plans for tonight?\n', 'textStyle': {}}}], 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 145, 'endIndex': 146, 'paragraph': {'elements': [{'startIndex': 145, 'endIndex': 146, 'textRun': {'content': '\n', 'textStyle': {}}}], 'paragraphStyle': {'headingId': 'h.x2a03jgebjrh', 'namedStyleType': 'HEADING_1', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 146, 'endIndex': 165, 'paragraph': {'elements': [{'startIndex': 146, 'endIndex': 165, 'textRun': {'content': 'Technology Inquiry\n', 'textStyle': {}}}], 'paragraphStyle': {'headingId': 'h.vwvivb1t3aps', 'namedStyleType': 'HEADING_1', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 165, 'endIndex': 393, 'paragraph': {'elements': [{'startIndex': 165, 'endIndex': 393, 'textRun': {'content': "Just watched the videos, that's sick! So, is it live on your phone? Do you need to message or forward messages to a specific number, or if I text you, will it categorize and create a document for this conversation, for example?\n", 'textStyle': {}}}], 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 393, 'endIndex': 394, 'paragraph': {'elements': [{'startIndex': 393, 'endIndex': 394, 'textRun': {'content': '\n', 'textStyle': {}}}], 'paragraphStyle': {'headingId': 'h.4gm5caif0ni', 'namedStyleType': 'HEADING_1', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 394, 'endIndex': 419, 'paragraph': {'elements': [{'startIndex': 394, 'endIndex': 419, 'textRun': {'content': 'Real Estate Transactions\n', 'textStyle': {}}}], 'paragraphStyle': {'headingId': 'h.pm0grojsaooo', 'namedStyleType': 'HEADING_1', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 419, 'endIndex': 453, 'paragraph': {'elements': [{'startIndex': 419, 'endIndex': 453, 'textRun': {'content': 'Went to show the land to Alfredo.\n', 'textStyle': {}}}], 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 453, 'endIndex': 454, 'paragraph': {'elements': [{'startIndex': 453, 'endIndex': 454, 'textRun': {'content': '\n', 'textStyle': {}}}], 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}}}]
        category = 'Real Estate Transactions'
        text = 'Need to parcel out some land.'
        
        expected_output = {
            "requests": [{'insertText': {'location': {'index': 453}, 'text': 'Need to parcel out some land.\n'}}, {'updateParagraphStyle': {'range': {'startIndex': 453, 'endIndex': 483}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'}, 'fields': 'namedStyleType'}}]
        }
        output = create_update_requests(doc_content, category, text)

        self.assertEqual(output, expected_output, '\n' + '\n'.join(difflib.ndiff(
                    json.dumps(expected_output, indent=2).splitlines(),
                    json.dumps(output, indent=2).splitlines()
                 )))
  
    def test_create_update_requests_existing_category_end_of_document_no_trailing_newline(self):
        doc_content = [
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
            "endIndex": 24,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 1,
                  "endIndex": 24,
                  "textRun": {
                    "content": "Financial Transactions\n",
                    "textStyle": {}
                  }
                }
              ],
              "paragraphStyle": {
                "headingId": "h.j8f7cok0s5ox",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
              }
            }
          },
          {
            "startIndex": 24,
            "endIndex": 54,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 24,
                  "endIndex": 54,
                  "textRun": {
                    "content": "Please give Austin 300 pesos.\n",
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
            "startIndex": 54,
            "endIndex": 87,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 54,
                  "endIndex": 87,
                  "textRun": {
                    "content": "Please transfer 500 pesos to Ty.\n",
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
            "startIndex": 87,
            "endIndex": 88,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 87,
                  "endIndex": 88,
                  "textRun": {
                    "content": "\n",
                    "textStyle": {}
                  }
                }
              ],
              "paragraphStyle": {
                "headingId": "h.ymjyujutzmie",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
              }
            }
          },
          {
            "startIndex": 88,
            "endIndex": 101,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 88,
                  "endIndex": 101,
                  "textRun": {
                    "content": "Social Plans\n",
                    "textStyle": {}
                  }
                }
              ],
              "paragraphStyle": {
                "headingId": "h.ili04vc9w7k3",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
              }
            }
          },
          {
            "startIndex": 101,
            "endIndex": 145,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 101,
                  "endIndex": 145,
                  "textRun": {
                    "content": "Are we making any dinner plans for tonight?\n",
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
            "startIndex": 145,
            "endIndex": 146,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 145,
                  "endIndex": 146,
                  "textRun": {
                    "content": "\n",
                    "textStyle": {}
                  }
                }
              ],
              "paragraphStyle": {
                "headingId": "h.x2a03jgebjrh",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
              }
            }
          },
          {
            "startIndex": 146,
            "endIndex": 165,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 146,
                  "endIndex": 165,
                  "textRun": {
                    "content": "Technology Inquiry\n",
                    "textStyle": {}
                  }
                }
              ],
              "paragraphStyle": {
                "headingId": "h.vwvivb1t3aps",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
              }
            }
          },
          {
            "startIndex": 165,
            "endIndex": 393,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 165,
                  "endIndex": 393,
                  "textRun": {
                    "content": "Just watched the videos, that's sick! So, is it live on your phone? Do you need to message or forward messages to a specific number, or if I text you, will it categorize and create a document for this conversation, for example?\n",
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
            "startIndex": 393,
            "endIndex": 394,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 393,
                  "endIndex": 394,
                  "textRun": {
                    "content": "\n",
                    "textStyle": {}
                  }
                }
              ],
              "paragraphStyle": {
                "headingId": "h.4gm5caif0ni",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
              }
            }
          },
          {
            "startIndex": 394,
            "endIndex": 419,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 394,
                  "endIndex": 419,
                  "textRun": {
                    "content": "Real Estate Transactions\n",
                    "textStyle": {}
                  }
                }
              ],
              "paragraphStyle": {
                "headingId": "h.pm0grojsaooo",
                "namedStyleType": "HEADING_1",
                "direction": "LEFT_TO_RIGHT"
              }
            }
          },
          {
            "startIndex": 419,
            "endIndex": 453,
            "paragraph": {
              "elements": [
                {
                  "startIndex": 419,
                  "endIndex": 453,
                  "textRun": {
                    "content": "Went to show the land to Alfredo.\n",
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
        category = 'Real Estate Transactions'
        text = 'Need to parcel out some land.'
        
        expected_output = {
            "requests": [{'insertText': {'location': {'index': 452}, 'text': '\nNeed to parcel out some land.\n'}}, {'updateParagraphStyle': {'range': {'startIndex': 452, 'endIndex': 483}, 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT'}, 'fields': 'namedStyleType'}}]
        }
        output = create_update_requests(doc_content, category, text)

        self.assertEqual(output, expected_output, '\n' + '\n'.join(difflib.ndiff(
                    json.dumps(expected_output, indent=2).splitlines(),
                    json.dumps(output, indent=2).splitlines()
                 )))    
    
    def test_create_update_requests_new_category_no_trailing_newline(self):
        doc_content = [{'endIndex': 1, 'sectionBreak': {'sectionStyle': {'columnSeparatorStyle': 'NONE', 'contentDirection': 'LEFT_TO_RIGHT', 'sectionType': 'CONTINUOUS'}}}, {'startIndex': 1, 'endIndex': 18, 'paragraph': {'elements': [{'startIndex': 1, 'endIndex': 18, 'textRun': {'content': 'Debt Obligations\n', 'textStyle': {}}}], 'paragraphStyle': {'headingId': 'h.1wx06ntcwsy', 'namedStyleType': 'HEADING_1', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 18, 'endIndex': 48, 'paragraph': {'elements': [{'startIndex': 18, 'endIndex': 48, 'textRun': {'content': 'Owe 6000 pesos to ClimaVista.\n', 'textStyle': {}}}], 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 48, 'endIndex': 92, 'paragraph': {'elements': [{'startIndex': 48, 'endIndex': 92, 'textRun': {'content': 'Owe an additional 8000 pesos to ClimaVista.\n', 'textStyle': {}}}], 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 92, 'endIndex': 138, 'paragraph': {'elements': [{'startIndex': 92, 'endIndex': 138, 'textRun': {'content': 'Owe an additional 10,000 pesos to ClimaVista.\n', 'textStyle': {}}}], 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 138, 'endIndex': 139, 'paragraph': {'elements': [{'startIndex': 138, 'endIndex': 139, 'textRun': {'content': '\n', 'textStyle': {}}}], 'paragraphStyle': {'headingId': 'h.m5qp55wcfbml', 'namedStyleType': 'HEADING_1', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 139, 'endIndex': 157, 'paragraph': {'elements': [{'startIndex': 139, 'endIndex': 157, 'textRun': {'content': 'Programming Tasks\n', 'textStyle': {}}}], 'paragraphStyle': {'headingId': 'h.s8mp9xazjbek', 'namedStyleType': 'HEADING_1', 'direction': 'LEFT_TO_RIGHT'}}}, {'startIndex': 157, 'endIndex': 188, 'paragraph': {'elements': [{'startIndex': 157, 'endIndex': 188, 'textRun': {'content': 'I need to write some programs.\n', 'textStyle': {}}}], 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'direction': 'LEFT_TO_RIGHT'}}}]
        category = 'Real Estate Inquiries'
        text = 'Message Oscar regarding some real estate inquiries.'
        
        expected_output = {
          "requests": [
            {
              "insertText": {
                "location": {
                  "index": 187
                },
                "text": "\n"
              }
            },
            {
              "updateParagraphStyle": {
                "range": {
                  "startIndex": 187,
                  "endIndex": 188
                },
                "paragraphStyle": {
                  "namedStyleType": "NORMAL_TEXT"
                },
                "fields": "namedStyleType"
              }
            },
            {
              "insertText": {
                "location": {
                  "index": 188
                },
                "text": "\n"
              }
            },
            {
              "updateParagraphStyle": {
                "range": {
                  "startIndex": 188,
                  "endIndex": 189
                },
                "paragraphStyle": {
                  "namedStyleType": "NORMAL_TEXT"
                },
                "fields": "namedStyleType"
              }
            },
            {
              "insertText": {
                "location": {
                  "index": 189
                },
                "text": "Real Estate Inquiries\n"
              }
            },
            {
              "updateParagraphStyle": {
                "range": {
                  "startIndex": 189,
                  "endIndex": 212
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
                  "index": 211
                },
                "text": "Message Oscar regarding some real estate inquiries.\n"
              }
            },
            {
              "updateParagraphStyle": {
                "range": {
                  "startIndex": 211,
                  "endIndex": 264
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


if __name__ == '__main__':
    unittest.main()