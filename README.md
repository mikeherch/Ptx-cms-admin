# Ptx-admin
Paratext CMS apps for project administration.
For information on Paratext software go to https://pt8.paratext.org

These files comprise four python apps that can be executed from within Paratext 8 using Paratext's 
python API.
  * Show Projects HTML - This app will display a report in the user's default web browser showing a 
    list of the Paratexts projects on the user's computer with useful information about each project.
  * Show Project Users HTML - This app will a display a report in the user's default web browser showing a
    chart consisting of all Paratext projects on the user's computer and the Paratext users associated
    with each project.
  * Show Project Plan HTML - This app will display a report in the user's default web browser showing the 
    details of a project plan. The app will show either the project plan of the current project, or a 
    standard plan named by the user.
  * Lexicon Export As SFM - This app will display a report in the user's default text editor showing the
    contents of a project's interlinear lexicon, Lexicon.xml, in SFM format. The report can be saved as a
    file and imported into Flex.
  * XML File Filter (beta) - Filters an XML file by applying regular expressions, and optionally preforms  
    search and replace on the filtered results. The results appear in a text file, that the user can save as 
    an XML file. This app was designed for use by Paratext support personnel. THIS IS A BETA! The script lacks 
    internal error checking.
 
To install:
* Close Paratext application
* Download all files to the cms folder in the Paratext 8 project folder of the user's computer. For most users,
the path is C:\My Paratext 8 Projects\cms\.

To execute any CMS app:
* Start Paratext application
* Open a project
* From the Paratext 8 menu choose: Checking > Advanced > Admin, and then choose one of the apps;
  from the Paratext 9 project menu choose: Custom tools > Admin, and then choose one of the apps.
