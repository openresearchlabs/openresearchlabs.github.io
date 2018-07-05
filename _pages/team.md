---
title: "Team"
layout: gridlay
excerpt: "Open Research Labs: Team members"
sitemap: false
permalink: /team/
---



# Research team

**Welcome to contact us to discuss research/study positions and collaboration.** 

<!--Jump to [PhD students](#phd), [master and bachelor students](#master-and-bachelor-students), [alumni](#alumni), [administrative support](#administrative-support), [lab visitors](#lab-visitors).-->


Principal Investigator: Leo Lahti
------------------------

<img class='inset right' src='../images/teampic/Leo_Lahti2.jpg' title='Leo Lahti' alt='Photo' width='120px' />



- Academy of Finland Research Fellow 2016-2021  
- [University of Turku](https://www.utu.fi/en/units/sci/units/math/Pages/home.aspx), Finland. Docent/Adjunct Professor. Applied Mathematics.
- [Blueprint Genetics](https://blueprintgenetics.com/) - Scientific Advisor (AI & Machine Learning)
- [VIB/KU Leuven (Raes Lab)](http://www.kuleuven.be/wieiswie/en/unit/50000700), Belgium. Visiting Researcher  
- [Open Science work group](http://fi.okfn.org/wg/openscience/) of the Open Knowledge Finland (OKF). Founding member and former coordinator  
- Twitter: [@antagomir](https://twitter.com/antagomir)
- [ORCID: 0000-0001-5537-637X](http://orcid.org/0000-0001-5537-637X)
<img class='inset right' src='../images/orcid_qrcode_leolahti.png' title='Leo Lahti ORCID QR code' alt='Photo' width='40px' />
- [Google Scholar](https://tinyurl.com/ng6g6tk); [Scopus](https://www.scopus.com/authid/detail.uri?authorId=8679063700); [Univ. Turku Research Portal](https://research.utu.fi/converis/portal/Person/17607336?auxfun=&lang=en_GB); [TUHAT](https://tuhat.halvi.helsinki.fi/portal/en/persons/leo-mikael-lahti%285d23e9ba-1f39-42f0-b23b-77fe12413479%29.html); [ResearchGate](http://www.researchgate.net/profile/Leo_Lahti/); [ResearcherID: G-3170-2010](http://www.researcherid.com/rid/G-3170-2010); [ScienceOpen](https://www.scienceopen.com/user/statistics/leo_lahti); [CiteUlike](http://www.citeulike.org/author/Lahti:L); [PubMed](http://www.ncbi.nlm.nih.gov/sites/myncbi/collections/public/1VaRtFbzqhfLWsXzDa1c5CSQK); [Publon reviewer profile](https://publons.com/author/246930/leo-lahti#stats); [ImpactStory](https://impactstory.org/u/0000-0001-5537-637X); [Depsy research software impact](http://depsy.org/person/333684); [Loop](http://loop.frontiersin.org/people/295152/overview)

## PhD Students 
{% assign number_printed = 0 %}
{% for member in site.data.phds %}

{% assign even_odd = number_printed | modulo: 2 %}

{% if even_odd == 0 %}
<div class="row">
{% endif %}

<div class="col-sm-6 clearfix">
  <img src="{{ site.url }}{{ site.baseurl }}/images/teampic/{{ member.photo }}" class="img-responsive" width="25%" style="float: left" />
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









