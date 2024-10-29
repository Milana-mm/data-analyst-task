# data-analyst-task

-	Data Analyst Task

SCOPE
1.	Data Processing 
2.	Data Analysis 
3.	Prediction Model

STEPS
1.	Create Directories: data, temp
2.	Import source files into `./data`
3.	Import .py scripts 
4.	To run Data Processing (necessary for steps 5 and 6)
4.1.	Run `pre_processing.py` script
4.2.	In case you did not manage to successfully run `pre_processing.py` as 1st step of data processing did not work - comment rows 129-139 in `data_processing.py` script
4.3.	Run `data_processing.py`- script performs data cleaning and saves new cleaned files into `.temp` folder
5.	To run Data Analysis: 
5.1.	Run `data_analysis.py` script
6.	To run Prediction Model:
6.1.	Open `prediction_model.py` script
6.2.	Scroll to rows 98-120
6.3.	Input relevant data for prediction model
6.4.	Run the script

PROCESS OVERVIEW
0.	Assessment and Planning
After reviewing the data and understanding the task, it became clear that the project needs to be completed in several phases. The first phase is data cleaning, which is a prerequisite for the next steps: data analysis with visualization and predictive modelling. As this is my first Python-based project and Python was not part of my skillset yet, I was focused to explore technology and possibilities as much as possible.
1.	Data Processing - Data Cleaning
Defined and performed various data cleaning steps such as handling missing values (decided not to go with `df.dropna(inplace=True)` and remove only outliers), change data types, standardising values, removing special characters, whitespace removal, number and dates formatting. Also performed some data manipulation steps such as filtering data, adding new calculated columns, renaming current column names (to avoid having the same column names in all tables, or to make clearer those are to be used as foreign keys), adding new Id column as a primary key. Rows with outliers (date) are being removed to keep relevant data only. Here I made couple of assumptions: defined outliers in this case and interpretation of null values in some cases and populated missing values. Hardcoded mappings were used for some geo value.
The last step in this work scope was exporting data – saving cleaned new files to be used in next steps. I left comments in the code for each action performed for me to easier manage through code, but some of the comments are obsolete lines I used to test output and possibilities. I decided to keep some of them, so it provides more insights in work done.
1.1.	Note: Populated geolocation data from a separate file due to issues with `geopy.geocoders` during development. Pre-processing step was introduced as a workaround after longer time desperately trying to troubleshoot initial, more elegant, approach.
1.1.1.	Fun fact: Some Python functions were disrupted due to specific SSL certificates required for reading Serbian IDs, affecting `geolocator.geocode`. This issue, and occasional 403 errors, were resolved with workaround after extensive troubleshooting with references like this [GitHub discussion]( https://github.com/Sygil-Dev/sygil-webui/discussions/1325#discussioncomment-8150646) and Nominatim status checks: https://nominatim.org/release-docs/latest/api/Status/ . Besides this, sometimes error 403 can occur, so in case pre-processing step does not work, some lines from processing script should be removed.
1.2.	Room for improvement: 
1.2.1.	Implement geocode part of data cleaning into one wholesome script. Since impact of this is to have half automated process instead of fully automated one. Also, I expect this to enable lots of data analysis and visualisation possibilities that I’m yet to explore.
1.2.2.	Implement naming nomenclature – although in this case column names serve purpose, implementing naming nomenclature would be beneficial as long-term solution. 
1.2.3.	Some columns with brackets were not reformatted. A potential enhancement could involve separating values in one of these columns and analysing correlations.
2.	Data Analysis
Tables joined in star schema using left join. During this process, I concentrated on using Python to explore the data, which may not have been the most efficient approach. Each attempt took considerable time instead of allowing for a quicker basic data investigation. I made a deliberate choice to prioritize this method compared to using familiar tools, as my primary goal was to deepen my understanding of the tool I was using. 
2.1.	Data analysis and insights
Created couple of visuals – `data_analysis.py`script - report with charts to test visuals
DETAILS WHAT I CHECKED AND CONCLUSION
2.2.	Room for improvement:
2.2.1.	Experiment with various libraries for data analysis such as Matplotlib, Seaborn, Plotly, Scikit-learn, SciPy,  Geopandas…
3.	Prediction Model
This was the first time for me to work with predictive models, and it tool a lot of investigation on this topic. My previous knowledge was only that there are famous libraries for this topic as PyTorch and TensorFlow. I decided to use TensorFlow.
I must admit that at some point I was not sure what Im doing.
3.1.	Room for improvement: There is lot of room for improvement here, I am happy that my script is working. 
![](model_result.png)
4.	Conclusion 
After six days on this project, and an uneven time distribution: the first day focused on planning, the next two days on familiarizing myself with basic Python functions, and the remaining 3 days on intensive work. This experience confirmed that it is feasible to gain a foundational understanding of a new tool or technology within a week. My main focus was on understanding Python syntax and understand how libraries are utilized while implementing steps I had conceptually defined previously, rather than on producing the final output. Through this, I gained insights into multiple different Python concepts previously unfamiliar.
5.	References (some of those did not become part of the task solution)
•	https://www.w3schools.com/python/default.asp
•	https://matplotlib.org/
•	https://matplotlib.org/stable/gallery/lines_bars_and_markers/index.html
•	https://plotly.com/graphing-libraries/
•	https://en.wikipedia.org/wiki/TensorFlow
•	https://en.wikipedia.org/wiki/PyTorch
•	https://en.wikipedia.org/wiki/Correlation_coefficient
•	https://en.wikipedia.org/wiki/Euclidean_distance
•	https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.Rbf.html
•	https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.RBFInterpolator.html#scipy.interpolate.RBFInterpolator

