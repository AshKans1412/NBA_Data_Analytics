# HoopsHub: NBA Insights Platform

![DALL·E](https://github.com/AshKans1412/NBA_Data_Analytics/assets/71004480/7a9f14b1-229a-416e-b09c-2550176ec2b9)


## Welcome to the World of Basketball

Welcome to HoopsHub, the comprehensive platform for NBA enthusiasts, analysts, and fans. HoopsHub provides a real-time view into the world of the NBA, offering current player statistics, season insights, shot chart visualizations, detailed player comparisons, and daily match updates.

---

### Discover HoopsHub

Discover a comprehensive view of the NBA with HoopsHub: delve into current player and season statistics, visualize data through shot charts, compare players in detail, and stay updated with daily match scores.

![NBA Image](https://static01.nyt.com/images/2017/07/12/sports/12SUMMERLEAGUE-web1/12SUMMERLEAGUE-web1-videoSixteenByNineJumbo1600.jpg)

---

## Overview

HoopsHub: NBA Insights Platform provides real-time updates on live NBA scores and daily matches, with frequent refreshes for the latest information. The application also boasts a sophisticated visualization suite to showcase insightful analyses, complemented by detailed player statistics and comprehensive comparison features, encapsulating all the essentials for NBA fans and analysts in one dynamic platform.

---

## Link to Application

- Primary Instance Link: [HoopsHub Primary Instance](http://174.129.97.188:8501/)
- Secondary Instance Link: [HoopsHub Secondary Instance](https://ash-nba-1.streamlit.app/)

HoopsHub's primary front-end instance is hosted on AWS EC2, fully containerized with Docker to ensure a robust and scalable user experience. In the event of increased traffic or downtime, the architecture includes a secondary, backup instance deployed on Streamlit Cloud. This strategic setup allows for immediate redirection to the backup, maintaining uninterrupted service and high availability of the HoopsHub platform.

---

## Data Sources and Integration

**Curated dataset from multiple sources for comprehensive NBA analytics.**

### Live Game Data
- **nba_api**: Provides real-time data for live NBA matches, capturing scores, game dynamics, and player performance.

### Community Engagement Insights
- **Reddit Insights**: Analyzes top NBA discussions and fan sentiments, offering insights into the basketball community's pulse.

### Player Performance Metrics
- **Basketball Reference Site**: The main source for detailed player statistics. Data is web-scraped and transformed to provide analytical depth.
- **Custom REST API Development**: Enhances data accessibility and integration, enabling HoopsHub to seamlessly retrieve and display player metrics.

[More Information on REST API](https://github.com/AshKans1412/NBA-Analysis-API)

---

## Architecture Diagram

![Architecture Diagram](https://raw.githubusercontent.com/Kaushiknb11/Airflow_NBA/main/assets/Architecture_Diagram.png)

HoopsHub leverages a diverse array of data sources including nba_api for live NBA match updates, Reddit for top NBA discussions, and detailed player statistics scraped from a basketball reference site...

*For a detailed description of the architecture, see the provided link or document.*

---

## GitHub Code Repositories

- [NBA Analysis API](https://github.com/AshKans1412/NBA-Analysis-API)
- [Airflow for NBA Data](https://github.com/Kaushiknb11/Airflow_NBA)
- [NBA Data Analytics](https://github.com/AshKans1412/NBA_Data_Analytics)

---

## Gallery

### AWS Lambda
![AWS Lambda](https://raw.githubusercontent.com/Kaushiknb11/Airflow_NBA/main/assets/AWS_Lambda.jpeg)

### Amazon EventBridge
![Amazon EventBridge](https://raw.githubusercontent.com/Kaushiknb11/Airflow_NBA/main/assets/Amazon_EventBridge.jpeg)

### AWS S3 Bucket
![AWS S3 Bucket](https://raw.githubusercontent.com/Kaushiknb11/Airflow_NBA/main/assets/S3.jpeg)

### Heroku - NBA Analysis API
![Heroku - NBA Analysis API](https://raw.githubusercontent.com/Kaushiknb11/Airflow_NBA/main/assets/Heroku.jpeg)

### AWS EC2 Instances
![AWS EC2 Instances](https://raw.githubusercontent.com/Kaushiknb11/Airflow_NBA/main/assets/EC2_Instances.jpeg)

### Jenkins Server
![Jenkins Server](https://raw.githubusercontent.com/Kaushiknb11/Airflow_NBA/main/assets/Jenkins_Server.jpeg)

### Airflow for NBA Data ETL
![Airflow for NBA Data ETL](https://raw.githubusercontent.com/Kaushiknb11/Airflow_NBA/main/assets/Screen%20Shot%202023-12-18%20at%2012.19.52%20PM.png)

### RDS - Postgres
![RDS - Postgres](https://raw.githubusercontent.com/Kaushiknb11/Airflow_NBA/main/assets/Screen%20Shot%202023-12-17%20at%2012.42.29%20PM.png)

---
