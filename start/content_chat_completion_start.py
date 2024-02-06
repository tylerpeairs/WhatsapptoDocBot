# Import the JSON module to handle the JSON data
import json

# Provided Google Docs JSON data
google_docs_json_example_1 = {

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
        "endIndex": 16,
        "paragraph": {
          "elements": [
            {
              "startIndex": 1,
              "endIndex": 16,
              "textRun": {
                "content": "Money Received\n",
                "textStyle": {}
              }
            }
          ],
          "paragraphStyle": {
            "headingId": "h.e1m8oigbc93",
            "namedStyleType": "HEADING_1",
            "direction": "LEFT_TO_RIGHT"
          }
        }
      },
      {
        "startIndex": 16,
        "endIndex": 46,
        "paragraph": {
          "elements": [
            {
              "startIndex": 16,
              "endIndex": 46,
              "textRun": {
                "content": "Received 300 pesos from Tyler\n",
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
        "startIndex": 46,
        "endIndex": 52,
        "paragraph": {
          "elements": [
            {
              "startIndex": 46,
              "endIndex": 52,
              "textRun": {
                "content": "Legal\n",
                "textStyle": {}
              }
            }
          ],
          "paragraphStyle": {
            "headingId": "h.yi6mteyiqxog",
            "namedStyleType": "HEADING_1",
            "direction": "LEFT_TO_RIGHT"
          }
        }
      },
      {
        "startIndex": 52,
        "endIndex": 68,
        "paragraph": {
          "elements": [
            {
              "startIndex": 52,
              "endIndex": 68,
              "textRun": {
                "content": "Permit Problems\n",
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
        "startIndex": 68,
        "endIndex": 78,
        "paragraph": {
          "elements": [
            {
              "startIndex": 68,
              "endIndex": 78,
              "textRun": {
                "content": "Prospects\n",
                "textStyle": {}
              }
            }
          ],
          "paragraphStyle": {
            "headingId": "h.dpp1e43gbzqq",
            "namedStyleType": "HEADING_1",
            "direction": "LEFT_TO_RIGHT"
          }
        }
      },
      {
        "startIndex": 78,
        "endIndex": 108,
        "paragraph": {
          "elements": [
            {
              "startIndex": 78,
              "endIndex": 108,
              "textRun": {
                "content": "Tyler wants to see Ventanilla\n",
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
google_docs_json_example_2 = {
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
        "endIndex": 16,
        "paragraph": {
          "elements": [
            {
              "startIndex": 1,
              "endIndex": 16,
              "textRun": {
                "content": "Money Received\n",
                "textStyle": {}
              }
            }
          ],
          "paragraphStyle": {
            "headingId": "h.e1m8oigbc93",
            "namedStyleType": "HEADING_1",
            "direction": "LEFT_TO_RIGHT"
          }
        }
      },
      {
        "startIndex": 16,
        "endIndex": 46,
        "paragraph": {
          "elements": [
            {
              "startIndex": 16,
              "endIndex": 46,
              "textRun": {
                "content": "Received 300 pesos from Tyler\n",
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
        "startIndex": 46,
        "endIndex": 52,
        "paragraph": {
          "elements": [
            {
              "startIndex": 46,
              "endIndex": 52,
              "textRun": {
                "content": "Legal\n",
                "textStyle": {}
              }
            }
          ],
          "paragraphStyle": {
            "headingId": "h.yi6mteyiqxog",
            "namedStyleType": "HEADING_1",
            "direction": "LEFT_TO_RIGHT"
          }
        }
      },
      {
        "startIndex": 52,
        "endIndex": 68,
        "paragraph": {
          "elements": [
            {
              "startIndex": 52,
              "endIndex": 68,
              "textRun": {
                "content": "Permit Problems\n",
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
        "startIndex": 68,
        "endIndex": 78,
        "paragraph": {
          "elements": [
            {
              "startIndex": 68,
              "endIndex": 78,
              "textRun": {
                "content": "Prospects\n",
                "textStyle": {}
              }
            }
          ],
          "paragraphStyle": {
            "headingId": "h.dpp1e43gbzqq",
            "namedStyleType": "HEADING_1",
            "direction": "LEFT_TO_RIGHT"
          }
        }
      },
      {
        "startIndex": 78,
        "endIndex": 108,
        "paragraph": {
          "elements": [
            {
              "startIndex": 78,
              "endIndex": 108,
              "textRun": {
                "content": "Tyler wants to see Ventanilla\n",
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
        "startIndex": 108,
        "endIndex": 138,
        "paragraph": {
          "elements": [
            {
              "startIndex": 108,
              "endIndex": 138,
              "textRun": {
                "content": "Tyler wants to see Ventanilla\n",
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
        "endIndex": 149,
        "paragraph": {
          "elements": [
            {
              "startIndex": 138,
              "endIndex": 149,
              "textRun": {
                "content": "Money Owed\n",
                "textStyle": {}
              }
            }
          ],
          "paragraphStyle": {
            "headingId": "h.wct4dpsxjrpd",
            "namedStyleType": "HEADING_1",
            "direction": "LEFT_TO_RIGHT"
          }
        }
      },
      {
        "startIndex": 149,
        "endIndex": 155,
        "paragraph": {
          "elements": [
            {
              "startIndex": 149,
              "endIndex": 155,
              "textRun": {
                "content": "To-Do\n",
                "textStyle": {}
              }
            }
          ],
          "paragraphStyle": {
            "headingId": "h.x9s19picaxz8",
            "namedStyleType": "HEADING_1",
            "direction": "LEFT_TO_RIGHT"
          }
        }
      },
      {
        "startIndex": 155,
        "endIndex": 156,
        "paragraph": {
          "elements": [
            {
              "startIndex": 155,
              "endIndex": 156,
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
      },
      {
        "startIndex": 156,
        "endIndex": 157,
        "paragraph": {
          "elements": [
            {
              "startIndex": 156,
              "endIndex": 157,
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
      },
      {
        "startIndex": 157,
        "endIndex": 158,
        "paragraph": {
          "elements": [
            {
              "startIndex": 157,
              "endIndex": 158,
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



# Extract HEADING_1 texts from the provided JSON
heading_texts = extract_heading_1_text(google_docs_json_example_1)
heading_texts_2 = extract_heading_1_text(google_docs_json_example_2)
# Print the extracted texts
print(heading_texts)
print(heading_texts_2)
