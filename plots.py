import matplotlib.pyplot as plt
from postgres_client import PostgresClient

if __name__ == "__main__":
    messages_sent_per_day_query = \
            """
                SELECT DATE("dateSent") AS date, COUNT(*) AS messages_sent
                FROM logs
                GROUP BY date
                ORDER BY date ASC;
            """
    messages_sent_per_month_query = \
        """
            SELECT DATE_TRUNC('month', DATE("dateSent"))::date AS month, COUNT(*) AS messages_sent
            FROM logs
            GROUP BY DATE_TRUNC('month', DATE("dateSent"))
            ORDER BY month ASC;
        """
    customer_engagement_query = \
        """
            SELECT COUNT(*) AS message_count
            FROM logs
            WHERE direction = 'outbound-api'
            GROUP BY "to"
            ORDER BY message_count DESC;
        """
    top_ten_customers_query = \
        """
            SELECT "to" AS recipient, COUNT(*) AS message_count
            FROM logs
            WHERE direction = 'outbound-api'
            GROUP BY "to"
            HAVING COUNT(*) > 2
            ORDER BY message_count DESC;
        """
    
    # init client
    client = PostgresClient()
    # q1 shows messages sent per day
    df1 = client.query_to_dataframe(messages_sent_per_day_query)
    df1.plot(x="date", y="messages_sent")
    plt.xlabel("Date")
    plt.ylabel("Messages Sent")
    plt.title("SMS Messages Sent Per Day")
    plt.show()
    
    # q2 shoes messages sent per month
    df2 = client.query_to_dataframe(messages_sent_per_month_query)
    df2.plot(kind="barh", x="month", y="messages_sent")
    plt.xlabel("Messages Sent")
    plt.ylabel("Month")
    plt.title("SMS Messages Sent Per Month")
    plt.show()
    
    # q3 shows the top 10 customers based on SMS data
    df3 = client.query_to_dataframe(top_ten_customers_query)[1:11]
    df3["censored recipient"] = df3["recipient"].apply(lambda x: x[:-7] + "*******")
    df3.plot(kind="barh", x="censored recipient", y="message_count")
    plt.xlabel("Messages Sent")
    plt.ylabel("Customer")
    plt.title("Top Ten Message Recipients")
    plt.show()
    
    # close the connection at the end to save resources
    client.close()