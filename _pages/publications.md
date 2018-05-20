---
title: "Publications"
layout: gridlay
excerpt: "Lahti Lab -- Publications."
sitemap: false
permalink: /publications/
---


Publications
============

The complete bibliography is available in [BibTex](lahti.bib). You can find most papers and other outputs from [here](publications/), or just ask by email.


<!-- This is for altmetrics padges from http://www.altmetric.com/-->

<script type='text/javascript' src='https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js'></script>



## Selected work

{% bibliography --file lahti --query @*[status=highlight] %}

## Computational biology and biomedicine

{% bibliography --file lahti  --query @article[keywords!=dh && status!=other && status!=highlight] %}


## Digital humanities and computational social science

{% bibliography --file lahti  --query @article[keywords=dh && status!=highlight] %}
{% bibliography --file lahti  --query @*[keywords=openscience] %}


## Theses and assignments

For source material (LaTeX code, figures etc.) of these theses, see [Github](https://github.com/antagomir/thesis).

{% bibliography --file lahti  --query @*[status=thesis && status!=highlight] %}


## Technical reports and outreach

<!--{% bibliography --file lahti  --query @misc[status!=poster && status!=abstract && status!=thesis && howpublished!=blog && howpublished!=software] %}-->
{% bibliography --file lahti  --query @techreport[status!=thesis && howpublished!=blog && howpublished!=software && status!=highlight && keywords!=openscience] %}
{% bibliography --file lahti  --query @*[status=other && howpublished!=blog && howpublished!=software && status!=highlight && keywords!=openscience] %}
{% bibliography --file lahti  --query @*[status=abstract && status!=highlight && keywords!=openscience] %}


## Digital material

See the separate [code](../code/) and [media](../media/) pages.


<!--The material is presented to ensure timely dissemination of scholarly and technical work. While I aim to grant CC or other open source/copyleft licenses for the content wherever possible, kindly note that copyright in the external links and all rights therein are retained by authors or by other copyright holders.-->

