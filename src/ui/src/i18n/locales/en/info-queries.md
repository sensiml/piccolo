The query is used to select your sensor data from your project. If you need to filter out certain parts of your sensor data based on metadata or labels, you can specify that here.

### Creating a Query

You can create a new query with the session and labels you wish to use in your project

### Query Filter

If you are working with your sensor data and you discover certain events of interest are bad or not useful you can ignore them in your query by using the **Query Filter**. If you have ever used a database query before then this syntax may be familiar to you.

---
For Example:

If you wanted to ignore the **Vertical** events, you can add the filter:

```[Label] IN [Horizontal, Stationary]```

You can also filter the metadata values using the Query Filter. In the Slide Demo you can add a **Subject** filter:

```[Label] IN [Horizontal, Stationary] AND [Subject] IN [User001]```

This filter would only select the **Horizontal** and **Stationary** events done by **User001**

---

[See Documentation](https://sensiml.com/documentation/guides/getting-started/querying-data.html?target=_blank)