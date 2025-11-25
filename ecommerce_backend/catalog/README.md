# Overview of the Catalog App

The catalog app is a Django app that provides a RESTful API for managing products and categories in an e-commerce store.
==> The primary purpose of the catalog app is to manage all the product data and the structure used to organize it.

### 🎯 Key Responsibilities
The catalog app handles all API requests related to browsing and product data:

* **Product Listing**: Provides the data needed to show the homepage or a search results page.
* **Filtering & Sorting**: Allows users to narrow down items by price, category, availability, etc.
* **Inventory Status**: Tells the frontend whether an item is is_available and how much stock_quantity is left.