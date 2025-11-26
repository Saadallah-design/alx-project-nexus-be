# General Learnings

## When dealing with APIs
- if we created a model and serialized it for consumption by front end, we can add a layer of security to make key fields read-only by adding the following line to the serializer:
```python
read_only_fields = ('id', 'created_at', 'updated_at', 'sale_price')
```
- for the sale_price since defined by a property in the model, we need to calculate it dynamically 
- this calculation is done through:
```python
sale_price = property(lambda self: self.base_price - (self.base_price * self.discount_percentage / 100))
```