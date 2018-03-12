# electron-flask-app

This app create a multi level bill of material from data exported from SAP
A bill of materials or product structure (sometimes bill of material, BOM or associated list) is a list of the raw materials, sub-assemblies, intermediate assemblies, sub-components, parts and the quantities of each needed to manufacture an end product. 

A multi-level bill of materials (BOM), or referred as an indented BOM, is a bill of materials that lists the components, assemblies, and parts required to make a product. It provides a display of all items that are in parent-children relationships. When an item is a sub-component, unfinished part, etc., all of its components, including finished parts and raw materials, are also exhibited. A multi-level structure can be illustrated by a tree with several levels. In contrast, a single-level structure only consists of one level of children in components, assemblies and material.
With  pandas we was able to create a mutli level bill of material exploded up to 10 levels or more , by using tree structures and Breath first search to build those parent-children relationship


in addition to  the bill of material we have calculated how much quantity is required to produce an item, and how long it takes to produce an item.
with time and quantity known we was able to calculate the price of an product .

The app was buid as flask web application and compiled using pyinstaller and deployed as a desktop application using electronjs .
