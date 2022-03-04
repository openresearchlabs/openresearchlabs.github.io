# Turku Data Science Group website

The following README gives a quick glance on how to add information from data files to Turku Data Science Group Website.

## Editing the front page

The front page layout is determined in the following file: **./themes/hugo-universal-theme/layouts/index.html**

The partials-files that affect the front page (among other pages) are "head.html", "nav.html", "boxes.html" (Research, EDU, Code, Team items), "twitter.html" ("Tweets by openreslabs" section), "testimonials.html", "see_more.html", "clients.html" and "footer.html". Edit them in **./themes/hugo-universal-theme/layouts/partials**. Please note that partials-files are, in an ideal situation, supposed to be templates for dynamically generating the site. Using them to store static html can cause problems.

The Recent publications section of the front page is different from others in that it is edited from **/content/_index.md** file. Its place is defined as " .Content " in the abovementioned index.html file. The workflow of editing this file is similar to editing other .md files, such as information on Research-pages. See below for further instructions on using shortcodes to output information.

Some front page items (their order, enabling/disabling certain sections, some texts) are determined in **config.yaml**-document in the root folder.

## Add and edit team member information

Edit appropriate .yaml-files in data/team to add new team member information. The information will then be displayed in content/team.md file under the group specified by the .yaml-file name. For example, this will print information on all post-doc team members:

```
{{< team data="postdocs" >}}
```

Team member pictures should have face in center and should be **close to a square (1:1 aspect ratio)**. If no picture is provided a default placeholder image will be used. Add your picture in the folder **./static/img/teampic** and use a relative URL when pointing to the picture - see current .yaml-files for examples.

### Editing the templates and CSS files

The relevant files are located in themes/hugo-universal-theme/layouts folder:

- layouts/shortcodes/team.html
- layouts/partials/team_partial.html

If you wish to edit flex-container item styles, see themes/hugo-universal-theme/static/css folder and file: style.default.css and rows starting with ".flex-container" and ".flex-item-".

More information about flex-containers:
- [StackOverflow](https://stackoverflow.com/questions/64853394/how-to-add-text-at-the-bottom-of-each-flexbox)
- [Aligning Items in a Flex Container (MDN Web Docs)](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout/Aligning_Items_in_a_Flex_Container)
- [A Complete Guide to Flexbox (CSS-Tricks)](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)

## Convert .bib files to .json

The site uses GitHub Actions to convert a .bib-file to a .json-file. Please remember to push changes made in .bib-file to server for changes to take place.

The workflow can be edited in .github/workflows/bibtex2json.yml

Currently the workflow reacts to changes a single .bib file: content/publication_resources/bibtex/lahti.bib

The output can be found in data/publications folder.

## Print items from bibliography

Specific items from the jsonified bibliography can be printed by using custom shortcodes in .md files (not HTML files). In this example a single item that has the unique id (or key) "Salosensaari2021" is printed:

```
{{< articles id = "Salosensaari2021" >}}
```

The output should look something like this:

**Taxonomic signatures of cause-specific mortality risk in human gut microbiome** (title in bold)  
Salosensaari A, Laitinen V, Havulinna A, Meric G, Cheng S, Perola M, Valsta L, Alfthan G, Inouye M, Watrous J, Long T, Salido R, Sanders K, Brennan C, Humphrey G, Sanders J, Jain M, Jousilahti P, Salomaa V, Knight R, Lahti L & Niiranen T. (all authors listed, first names abbreviated)  
Nature Communications 12, 2021 (publication name, issue, year)  
[10.1038/s41467-021-22962-y](https://doi.org/10.1038/s41467-021-22962-y) (DOI and optional URL as a link)

If you wish to print all items that have a specific keyword (in this case "opinion"), use parameter "keyword":

```
{{< articles keyword = "opinion" >}}
```

Finally, ff you wish to print all items in the bibliography, simply use the shortcode with no parameters:

```
{{< articles >}}
```

### Editing the shortcodes and output styles

The relevant files are located in themes/hugo-universal-theme/layouts folder:

- layouts/shortcodes/articles.html
- layouts/partials/publications_partial.html

Especially if you want to change how output is formatted, see publications_partial.html.

For more information about shortcodes and partials, see following links: 
- [Hugo documentation](https://gohugo.io/templates/shortcode-templates/)
- For inspiration: loup-brun's [Hugo Cite](https://labs.loupbrun.ca/hugo-cite/)
