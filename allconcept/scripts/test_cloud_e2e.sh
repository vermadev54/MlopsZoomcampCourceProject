export KINESIS_STREAM_INPUT="stg_credit_profile_events-credit_card_profile_prediction"
export KINESIS_STREAM_OUTPUT="stg_credit_profile_predictions-credit_card_profile_prediction"

aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1  \
    --data '{"profile": {"Customer_Age": 45, "Gender": "M", "Dependent_count": 3, "Education_Level": "High School", "Marital_Status": "Married", "Income_Category": "$60K - $80K", "Card_Category": "Blue", "Months_on_book": 39, "Total_Relationship_Count": 5, "Months_Inactive_12_mon": 1, "Contacts_Count_12_mon": 3, "Credit_Limit": 12691.0, "Total_Revolving_Bal": 777, "Avg_Open_To_Buy": 11914.0, "Total_Amt_Chng_Q4_Q1": 1.335, "Total_Trans_Amt": 1144, "Total_Trans_Ct": 42, "Total_Ct_Chng_Q4_Q1": 1.625, "Avg_Utilization_Ratio": 0.061}, "profile_id": 100}'


SHARD="shardId-000000000001"

SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)


RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)

echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode
