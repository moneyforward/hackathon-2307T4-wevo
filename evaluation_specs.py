EVALUATIONS_DESCRIPTION = {
    "Company": {
        "Fulfillment": {
            "Description": "This measures how much employees feel their work is meaningful and fulfilling."
        },
        "Autonomy": {
            "Description": "This gauges the extent to which employees feel they have the freedom and independence to make decisions about their work."
        },
        "GrowthOpportunities": {
            "Description": "This measures how many opportunities for growth and development the company offers."
        },
        "Workload": {
            "Description": "This evaluates whether employees perceive their workload as manageable and balanced."
        },
        "Stress": {
            "Description": "This measures the level of stress employees experience in their work environment."
        },
        "WorkLifeBalance": {
            "Description": "This gauges how well employees are able to balance their work responsibilities with their personal life."
        },
    },
    "Person": {
        "Recognition": {
            "Description": "This evaluates how often the person is recognized and appreciated for their work."
        },
        "Sympathy": {
            "Description": "This gauges the extent to which colleagues feel empathetic and understanding towards the person."
        },
        "Trust": {
            "Description": "This measures how much trust and confidence colleagues place in the person."
        },
        "ProSupport": {
            "Description": "This measures how much professional support the person offers to their colleagues."
        },
        "GrowthSupport": {
            "Description": "This evaluates how much support the person provides to their colleagues in terms of growth and development opportunities."
        },
    }
}

EVALUATION_FUNCTIONS_SPEC = [
    {
        "name": "insert_evaluation",
        "description": "Process and store evaluation criteria for each given target",
        "parameters": {
            "type": "object",
            "properties": {
                "evaluations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "EvaluationTargetType": {"type": "integer",
                                                     "description": "Type of target: 1=Company 2=Person"},
                            "SubjectUserID": {"type": "string", "description": "Person ID"},
                            "SubjectName": {"type": "string", "description": "Person name"},
                            "Company_Fulfillment": {"type": "integer", "description": "Score for company fulfillment"},
                            "Company_FulfillmentWeight": {"type": "number",
                                                          "description": "Weight for company fulfillment score"},
                            "Company_Autonomy": {"type": "integer", "description": "Score for company autonomy"},
                            "Company_AutonomyWeight": {"type": "number",
                                                       "description": "Weight for company autonomy score"},
                            "Company_GrowthOpportunities": {"type": "integer",
                                                            "description": "Score for company growth opportunities"},
                            "Company_GrowthOpportunitiesWeight": {"type": "number",
                                                                  "description": "Weight for company growth opportunities score"},
                            "Company_Workload": {"type": "integer", "description": "Score for company workload"},
                            "Company_WorkloadWeight": {"type": "number",
                                                       "description": "Weight for company workload score"},
                            "Company_Stress": {"type": "integer", "description": "Score for company stress"},
                            "Company_StressWeight": {"type": "number",
                                                     "description": "Weight for company stress score"},
                            "Company_WorkLifeBalance": {"type": "integer",
                                                        "description": "Score for company work life balance"},
                            "Company_WorkLifeBalanceWeight": {"type": "number",
                                                              "description": "Weight for company work life balance score"},
                            "Person_Recognition": {"type": "integer", "description": "Score for person recognition"},
                            "Person_RecognitionWeight": {"type": "number",
                                                         "description": "Weight for person recognition score"},
                            "Person_Sympathy": {"type": "integer", "description": "Score for person sympathy"},
                            "Person_SympathyWeight": {"type": "number",
                                                      "description": "Weight for person sympathy score"},
                            "Person_Trust": {"type": "integer", "description": "Score for person trust"},
                            "Person_TrustWeight": {"type": "number", "description": "Weight for person trust score"},
                            "Person_ProSupport": {"type": "integer", "description": "Score for professional support"},
                            "Person_ProSupportWeight": {"type": "number",
                                                        "description": "Weight for professional support score"},
                            "Person_GrowthSupport": {"type": "integer", "description": "Score for growth support"},
                            "Person_GrowthSupportWeight": {"type": "number",
                                                           "description": "Weight for growth support score"},
                            "SentimentData": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "word": {"type": "string", "description": "The word of sentiment"},
                                        "weight": {"type": "number",
                                                   "description": "decimal: 0 is negative, 1 is positive"},
                                        "count": {"type": "integer",
                                                  "description": "number of appearance"}
                                    },
                                    "required": [
                                        "word",
                                        "weight",
                                        "count"
                                    ]
                                }
                            },
                        },
                        "required": [
                            "EvaluationTargetType",
                            "SubjectUserID",
                            "SubjectUserName",
                            "Company_Fulfillment",
                            "Company_FulfillmentWeight",
                            "Company_Autonomy",
                            "Company_AutonomyWeight",
                            "Company_GrowthOpportunities",
                            "Company_GrowthOpportunitiesWeight",
                            "Company_Workload",
                            "Company_WorkloadWeight",
                            "Company_Stress",
                            "Company_StressWeight",
                            "Company_WorkLifeBalance",
                            "Company_WorkLifeBalanceWeight",
                            "Person_Recognition",
                            "Person_RecognitionWeight",
                            "Person_Sympathy",
                            "Person_SympathyWeight",
                            "Person_Trust",
                            "Person_TrustWeight",
                            "Person_ProSupport",
                            "Person_ProSupportWeight",
                            "Person_GrowthSupport",
                            "Person_GrowthSupportWeight"
                        ]
                    }
                }
            },
        },
    }
]
