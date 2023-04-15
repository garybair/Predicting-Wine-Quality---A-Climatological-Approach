# Predicting Wine Quality - A Climatological Approach
Since the inception of climate change, ecologists have attempted to project the outcomes of altered global weather patterns and the resulting impacts on human society. Among these projected outcomes, a shift in the habitable geographic ranges of plant-based organisms presents as a notable threat to wine producers given the integration between growing conditions and the quality of the final product. One solution proposed by ecologists is the relocation of impacted species to new geographic regions, however the application of this solution in the context of the wine industry requires determining whether critical wine ratings can be modelled as a function of weather features.

To address this question, wine listing data was scraped from Wine.com and, using parsed origin and vintage data, was cross walked to generate historical weather data from Weather Underground. Machine learning algorithms were then developed to predict critical wine review scores and identify key predictive weather features.


### Table of Contents
- [Installation](https://github.com/garybair/Wine-Rating-Projections-Using-Historic-Weather-Patterns###Installation)
- [Usage](https://github.com/garybair/Wine-Rating-Projections-Using-Historic-Weather-Patterns###Usage)
- [Data](https://github.com/garybair/Wine-Rating-Projections-Using-Historic-Weather-Patterns###Data)
- [Contributing](https://github.com/garybair/Wine-Rating-Projections-Using-Historic-Weather-Patterns###Contributing)
- [License](https://github.com/garybair/Wine-Rating-Projections-Using-Historic-Weather-Patterns###License)

### Installation
To install this code, you will need to have Python 3 installed on your computer. You can then clone this repository and install the required dependencies using the following command:
```
pip install -r requirements.txt
```

### Usage
Jupyter Notebooks are numbered in the order of development with data acquisition and preprocessing notebooks being order dependent.

### Data
The product listing data utilized in this analysis was retrieved from Wine.com on March 14th, 2023 and historic weather data was sourced from Weather Underground’s historic weather search engine. Both datasets are included in this repository under the data directory.

### Contributing
If you would like to contribute to this project, please submit a pull request. We welcome contributions from anyone!

### License
This project is licensed under the MIT License - see the LICENSE.md file for details.
