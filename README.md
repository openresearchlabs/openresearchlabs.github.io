# Turku Data Science Group website

## Add and edit team member information

Edit appropriate .yaml-files in data/team to add new team member information. The information will then be displayed in content/team.md file under the group specified by the .yaml-file name. For example, this will print information on all post-doc team members:

{{< team data="postdocs" >}}

Team member pictures should have face in center and should be close to a square. If no picture is provided a default placeholder image will be used. Add your picture in folder ./static/img/teampic and use a relative URL when pointing to the picture.

### Editing the templates and CSS files

The relevant files are located in themes/hugo-universal-theme/layouts folder:

- layouts/shortcodes/team.html
- layouts/partials/team_partial.html

If you wish to edit flex-container item styles, see themes/hugo-universal-theme/static/css folder and file: style.default.css and rows starting with ".flex-container" and ".flex-item-".

More information about flex-containers:
- [StackOverflow](https://stackoverflow.com/questions/64853394/how-to-add-text-at-the-bottom-of-each-flexbox)
- [Aligning Items in a Flex Container (MDN Web Docs)](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout/Aligning_Items_in_a_Flex_Container)
- [A Complete Guide to Flexbox (CSS-Tricks)](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)

## Print items from bibliography

The site uses GitHub Actions to convert a .bib-file to a .json-file. Please remember to push changes made in .bib-file to server for changes to take place.

Specific items from the bibliography can be printed by using custom shortcodes in .md files (not HTML files). In this example a single item that has the unique id (or key) "Salosensaari2021" is printed:

{{< articles id = "Salosensaari2021" >}}

The output would look like this:

**Taxonomic signatures of cause-specific mortality risk in human gut microbiome**
Salosensaari* A, Laitinen* V, Havulinna A, Meric G, Cheng S, Perola M, Valsta L, Alfthan G, Inouye M, Watrous J, Long T, Salido R, Sanders K, Brennan C, Humphrey G, Sanders J, Jain M, Jousilahti P, Salomaa V, Knight R, Lahti* L & Niiranen* T. 
Nature Communications 12, 2021
[10.1038/s41467-021-22962-y](https://doi.org/10.1038/s41467-021-22962-y)

If you wish to print all items that have a specific keyword (in this case "opinion"), use parameter "keyword" like this:

{{< articles keyword = "opinion" >}}

Finally, ff you wish to print all items in the bibliography, simply use the shortcode with no parameters:

{{< articles >}}

### Editing the shortcodes and output styles

The relevant files are located in themes/hugo-universal-theme/layouts folder:

- layouts/shortcodes/articles.html
- layouts/partials/publications_partial.html

For more information about shortcodes and partials, see following links: 
- [Hugo documentation](https://gohugo.io/templates/shortcode-templates/)
- For inspiration: loup-brun's [Hugo Cite](https://labs.loupbrun.ca/hugo-cite/)