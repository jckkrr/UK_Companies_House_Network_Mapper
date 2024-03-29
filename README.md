# UK Companies House Network Mapper
Scrapes data from the Comanies House website to build a network map of a company's officers and persons with significant control, to see how interconnected their interests are. 

![image](https://user-images.githubusercontent.com/69304112/208015336-ab10718d-9b7e-43e7-9734-21a86894e45e.png)

At the heart of this is two basic scripts: one to harvest a list of all the companies a person is an officer of; the other to compile a list of all the officers and persons of significant interest that a company has.

Another script, built off the PyVis library, then converts these into interactive network maps. Active directors are green. Resigned/inactive directors are greyed out. A node cna be highighted (orange) but adding its identifier code into the function callback.

![image](https://user-images.githubusercontent.com/69304112/208037675-4dd81ad8-75dc-43e8-9dfa-55b07df23e06.png)

These basic scripts can be then be used to build dataframes of groups of companies, by entering the list of all company ids. 

Another script takes one company id, finds all persons associated with it, then finds their other associated companies and the other people that it has as officers of PSCs. 

These bigger dataframes then allow for intersting analyses - such as checking for any connections between two groups of companies.

![image](https://user-images.githubusercontent.com/69304112/209260285-cda1a131-350e-43e7-b890-47572a6886dd.png)
