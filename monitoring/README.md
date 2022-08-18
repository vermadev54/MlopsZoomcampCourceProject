
# Monitoring

## Prerequisites

You need following tools installed:
- `docker`
- `docker-compose` (included to Docker Desktop for Mac and Docker Desktop for Windows )

## Preparation

Note: all actions expected to be executed in repo folder.

- Create virtual environment and activate it (eg. `python -m venv venv && source ./venv/bin/activate`)
- Install required packages `pip install -r requirements.txt`

## Monitoring Example

### Starting services

To start all required services, execute:
```bash
docker-compose up
```

It will start following services:
- `prometheus` - TSDB for metrics
- `grafana` - Visual tool for metrics
- `mongo` - MongoDB, for storing raw data, predictions, targets and profile reports
- `evidently_service` - Evindently RT-monitoring service (draft example)
- `prediction_service` - main service, which makes predictions


## Batch Monitoring Example

After you stop sending data to service, you can run batch monitoring pipeline (using Prefect) by running script:

```bash
python prefect_example.py
```

This script will:
- load `target.csv` to MongoDB
- download dataset from MongoDB
- Run Evidently Model Profile and Evidently Report on this data
- Save Profile data back to MongoDB
- Save Report to `evidently_report_credit_card_card.html`

You can look at Prefect steps in Prefect Orion UI
(to start it execute `prefect orion start --host 0.0.0.0`)

Open the newly created Evidently HTML file to find the report along with visualizations

![](/MlopsZoomcampCourceProject/monitoring/image/Screenshot%202022-08-18%20at%204.09.36%20PM.png)

![](/MlopsZoomcampCourceProject/monitoring/image/Screenshot%202022-08-18%20at%204.09.58%20PM.png)

![](/MlopsZoomcampCourceProject/monitoring/image/Screenshot%202022-08-18%20at%204.10.15%20PM.png)
