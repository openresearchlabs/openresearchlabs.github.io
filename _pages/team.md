---
title: "Team"
layout: gridlay
excerpt: "Lahti Lab: Team members"
sitemap: false
permalink: /team/
---



# Research team

**You are welcome to contact us to discuss research/study positions and collaboration (BSc/MSc/PhD/Postdoc).** 

<!--Jump to [PhD students](#phd), [master and bachelor students](#master-and-bachelor-students), [alumni](#alumni), [administrative support](#administrative-support), [lab visitors](#lab-visitors).-->


Principal Investigator: Leo Lahti
------------------------

<img class='inset right' src='../images/teampic/Leo_Lahti.jpg' title='Leo Lahti' alt='Photo' width='120px' />

- Academy of Finland Research Fellow 2016-2021  
- [University of Turku](https://www.utu.fi/en/units/sci/units/math/Pages/home.aspx), Finland. Docent/Adjunct Professor. Applied Mathematics.
- [Blueprint Genetics](https://blueprintgenetics.com/) - Scientific Advisor (AI & Machine Learning)
- [VIB/KU Leuven](http://www.kuleuven.be/wieiswie/en/unit/50000700), Belgium. Visiting Researcher  
- [Open Science work group](http://fi.okfn.org/wg/openscience/) of the Open Knowledge Finland (OKF). Founding member and former coordinator  
- Twitter: [@antagomir](https://twitter.com/antagomir)


## PhD Students 
{% assign number_printed = 0 %}
{% for member in site.data.phds %}

{% assign even_odd = number_printed | modulo: 2 %}

{% if even_odd == 0 %}
<div class="row">
{% endif %}

<div class="col-sm-6 clearfix">
  <h4>{{ member.name }}</h4>
  <i>{{ member.info }}<br>email: <{{ member.email }}></i>
  <ul style="overflow: hidden">
  
  {% if member.number_educ == 1 %}
  <li> {{ member.education1 }} </li>
  {% endif %}
  
  {% if member.number_educ == 2 %}
  <li> {{ member.education1 }} </li>
  <li> {{ member.education2 }} </li>
  {% endif %}
  
  {% if member.number_educ == 3 %}
  <li> {{ member.education1 }} </li>
  <li> {{ member.education2 }} </li>
  <li> {{ member.education3 }} </li>
  {% endif %}
  
  {% if member.number_educ == 4 %}
  <li> {{ member.education1 }} </li>
  <li> {{ member.education2 }} </li>
  <li> {{ member.education3 }} </li>
  <li> {{ member.education4 }} </li>
  {% endif %}
  
  </ul>
</div>

{% assign number_printed = number_printed | plus: 1 %}

{% if even_odd == 1 %}
</div>
{% endif %}

{% endfor %}

{% assign even_odd = number_printed | modulo: 2 %}
{% if even_odd == 1 %}
</div>
{% endif %}





## Undergraduate Students 
{% assign number_printed = 0 %}
{% for member in site.data.students %}

{% assign even_odd = number_printed | modulo: 2 %}

{% if even_odd == 0 %}
<div class="row">
{% endif %}

<div class="col-sm-6 clearfix">
  <h4>{{ member.name }}</h4>
  <i>{{ member.info }}<br>email: <{{ member.email }}></i>
  <ul style="overflow: hidden">
  
  {% if member.number_educ == 1 %}
  <li> {{ member.education1 }} </li>
  {% endif %}
  
  {% if member.number_educ == 2 %}
  <li> {{ member.education1 }} </li>
  <li> {{ member.education2 }} </li>
  {% endif %}
  
  {% if member.number_educ == 3 %}
  <li> {{ member.education1 }} </li>
  <li> {{ member.education2 }} </li>
  <li> {{ member.education3 }} </li>
  {% endif %}
  
  {% if member.number_educ == 4 %}
  <li> {{ member.education1 }} </li>
  <li> {{ member.education2 }} </li>
  <li> {{ member.education3 }} </li>
  <li> {{ member.education4 }} </li>
  {% endif %}
  
  </ul>
</div>

{% assign number_printed = number_printed | plus: 1 %}

{% if even_odd == 1 %}
</div>
{% endif %}

{% endfor %}

{% assign even_odd = number_printed | modulo: 2 %}
{% if even_odd == 1 %}
</div>
{% endif %}




## Former students

**PhD Students** Jose Caldas (With Prof Samuel Kaski; Aalto 2012)

**Master Students** Hege Roivainen (Helsinki 2017); Marnix Denys (KU Leuven 2017); Tineka Blake (Wageningen 2015); Emilio Ugaldes Morales (Wageningen 2014)  

<!--**Bachelor Students** Maija Nevala (TKK 2008); Jyry Suvilehto (TKK 2007)-->
 
   

<!--
## Administrative Support
<a href="mailto:support@utu.fi">N.N</a> is helping us. and other groups) with administration.
-->




Material
---------------------------

Resources and tips on responsible research, journals and conferences, and other info are being collected [here](resources.html)









