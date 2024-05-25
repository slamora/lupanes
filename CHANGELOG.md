# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## main

## 0.1.2 - 2024-05-25
- [added] PWA
- [added] `tienda` Export albaranes list.
- [added] #15 Current customer balance.
- [fixed] #13 Handle error if there is no price for a product on a specific date.

## 0.1.1 - 2023-06-16
- [fixed] Regenerate users initial migration (changed user manager).

## 0.1.0 - 2023-06-16
First release! Created basic features to manage delivery notes:
- [added] Users login and permission system (based on `neveras` and `tienda` groups).
- [added] Register, update and delete new delivery notes.
- [added] `neveras`: List my delivery notes (archive by months).
- [added] `neveras`: Notify missing product on delivery notes product selector.
- [added] `tienda`: List and summary of delivery notes (archive by months).
- [added] `tienda`: List customers.
- [added] `tienda`: Manage products and their prices.
