USE wevo;

CREATE TABLE Companies
(
    ID   VARCHAR(32) PRIMARY KEY,
    Name VARCHAR(255)
);

CREATE TABLE Users
(
    ID        VARCHAR(32) PRIMARY KEY,
    Name      VARCHAR(255),
    CompanyID VARCHAR(32),
    FOREIGN KEY (CompanyID) REFERENCES Companies (ID)
);

CREATE TABLE UserRelations
(
    ID           VARCHAR(32) PRIMARY KEY,
    UserID1      VARCHAR(32),
    UserID2      VARCHAR(32),
    Relationship VARCHAR(255), -- Can be 'Colleague', 'Superior', etc.
    FOREIGN KEY (UserID1) REFERENCES Users (ID),
    FOREIGN KEY (UserID2) REFERENCES Users (ID)
);


CREATE TABLE SlackUsers
(
    ID     VARCHAR(32) PRIMARY KEY,
    UserID VARCHAR(32),
    FOREIGN KEY (UserID) REFERENCES Users (ID)
);

CREATE TABLE Feedback
(
    ID           VARCHAR(32) PRIMARY KEY,
    UserID       VARCHAR(32),
    TargetUserID VARCHAR(32),
    Timestamp    DATETIME,
    Data         TEXT,
    IsCalculated BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (UserID) REFERENCES Users (ID),
    FOREIGN KEY (TargetUserID) REFERENCES Users (ID)
);

CREATE TABLE Evaluation
(
    ID                                VARCHAR(32) PRIMARY KEY,
    FeedbackID                        VARCHAR(32),
    EvaluationTargetType              INTEGER,      -- 1=Company 2=Known Person 3=Unknown Person
    TargetUserName                    VARCHAR(255), -- To store unknown user name (Type 3)
    TargetUserID                      VARCHAR(32),  -- To store known person ID (Type 2)
    UserID                            VARCHAR(32),
    Timestamp                         DATETIME,
    -- Company assessment (Type 1)
    Company_Fulfillment               INT,
    Company_FulfillmentWeight         DECIMAL(5, 2),
    Company_Autonomy                  INT,
    Company_AutonomyWeight            DECIMAL(5, 2),
    Company_GrowthOpportunities       INT,
    Company_GrowthOpportunitiesWeight DECIMAL(5, 2),
    Company_Workload                  INT,
    Company_WorkloadWeight            DECIMAL(5, 2),
    Company_Stress                    INT,
    Company_StressWeight              DECIMAL(5, 2),
    Company_WorkLifeBalance           INT,
    Company_WorkLifeBalanceWeight     DECIMAL(5, 2),
    -- Person assessment (Type 2 & 3)
    Person_Recognition                INT,
    Person_RecognitionWeight          DECIMAL(5, 2),
    Person_Sympathy                   INT,
    Person_SympathyWeight             DECIMAL(5, 2),
    Person_Trust                      INT,
    Person_TrustWeight                DECIMAL(5, 2),
    Person_ProSupport                 INT,
    Person_ProSupportWeight           DECIMAL(5, 2),
    Person_GrowthSupport              INT,
    Person_GrowthSupportWeight        DECIMAL(5, 2),

    SentimentData  TEXT, -- Json array [{"word": $string, "weight": $weight}], $weight = -1 negative <-> positive 1


    FOREIGN KEY (UserID) REFERENCES Users (ID),
    FOREIGN KEY (FeedbackID) REFERENCES Feedback (ID)
);

INSERT INTO Companies (ID, Name) VALUE (0, 'Everything Forward');
