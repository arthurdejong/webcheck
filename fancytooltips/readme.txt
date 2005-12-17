FancyTooltips

Version: 1.2.1

Description:

FancyTooltips is a WordPress Plugin and General Script that dynamically changes the 
tooltips that are created by browsers. Basically, FancyTooltips replaces those 
boring little boxes that appear next to your mouse with a dynamic and impressive one. 
FancyTooltips supports the title attribute from anchors (<a>), acronyms (<acronym>), 
inserts (<ins>), and deletions (<del>) and the alt attribute from images (<img />). 
It will also display the accesskey attribute from an anchor (<a>).

How To Install:

   1. Download the Regular Script file.
   2. Extract the files.
   3. Upload them to where the index of your website is located (do not alter the 
	structure)
   4. Here’s the tricky part: Add the following to code in between your <head></head> 
	tags:

      <script language="javascript" type="text/javascript" src="./fancytooltips/fancytooltips.js"></script>
      <link rel=”stylesheet” href=”./fancytooltips/fancytooltips.css” type=”text/css” media=”screen” />

      Note: You will need to edit the URI of the files if you alter the structure or 
	if you want the FancyTooltips to display on a page that is located in a 
	subdirectory.

Usage:

It’s simple to use. Once installed, all you need to do is add: title="This is the content 
of the FancyTooltips" attribute to anchors (<a>), acronyms (<acronym>), inserts (<ins>), 
and deletions (<del>) or the alt="This is the content of the FancyTooltips" attribute to 
images (<img />) (image FancyTooltips are turned off by default). It will also display 
access keys within the FancyTooltips, simple enter in the accesskey="a" attribute into an
anchor (<a>).

Explanation:

There isn’t much to explain. Everytime you have a title (or, in <img />, an alt) attribute 
in your code, the script will replace them with aFancyTooltip! There isn’t much more 
than that.

Customization:

You can customize the colours of the FancyTooltips by editing the “fancytooltips.css” file. 
For those of you who are CSS savvy, I suggest W3Schools. There is description of what each
style in the fancytooltips.css does.

You can turn on the <img /> recognition feature by remove /* */ from the fancytooltips.js
file on line 399. Note: Remove /* */ from the first line, not the second.

By default, FancyTooltips are created throughout the entire webpage. If you wish to have
FancyTooltips restricted to a certain ID container (e.g. <div id="content">) simply add
the specified ID in between '' on line 27.

Change Log:

v.1.2.1 - Fixed:
- BIG CSS BUG.

v.1.2 - Added:
- ID restriction.
- Help cursors for <abbr>, <acronym>, <del>, and <ins>.
v.1.2 - Removed:
- <img> FancyTooltips turned off by default.
v.1.2 - Improved: 
- CSS semi-descriptions.

v1.1 (Beta Release) - Removed:
- Single file package.

v.1.0 (Private Alpha) - No Information

Licence:

As originally released by Stuart Langridge, this script is licensed under the MIT License.

Special Thanks:

This script was based on NiceTitles by Dunstan Orchard and Stuart Langridge.

Also, a big thank you to Brett Taylor for his help with the WordPress Plugin implementation.
And Chris Beaven for the ID restriction code.