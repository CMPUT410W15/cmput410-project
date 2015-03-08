# SocialDistribution API Doc

## Contents

### Posts

 - Get all posts visible to the currently authenticated user.
 - Get all posts marked as public on the server.
 - Get all posts by a specific author visible to the currently authenticated user.
 - Get a specific single post.
 - Add a comment to a post.

### Friends

- Get all authors on host.
- Get information and connections about one author on host.
- Query whether one author is following another.
- Query whether which members of a list of authors are following a specified author.
- Get the authors on the host following a specific author on a specific host.
 
## API Requirements

### Endpoint

All URIs in this document are located at the endpoint: `http://cs410.cs.ualberta.ca:41081/api/`. 

All requests must make use of HTTP Basic Auth using a username and password negotiated at time of server setup.

### Objects

The objects returned by the methods of the API are specified below in commented JSON format.

- **Author:** An author is the user entity on the host.  An author is associated with one host and has a username that is unique on that host.
```
      {
	    # unique id to each author, either a sha1 or a uuid
		"id":"9de17f29c12e8f97bcbbd34cc908f1baba40658e",
        # the home host of the author
		"host":"http://127.0.0.1:5454/",
		# the display name of the author
		"displayname":"Lara"
      }
```


- **Post:** Authors create posts which contain optionally a text body and image.

```
      {
	    # A list of posts
		"posts":[
		  {
            # title of a post
		    "title":"A post title about a post about web dev",
		    # a brief description of the post
		    "description":"This post discusses stuff -- brief",
		    # an image URL
		    "image": "imageURL",
		    # The content type of the post
		    # assume either
		    # text/x-markdown
		    # text/plain
		    "content-type":"text/plain",
		    "content":"Þā wæs on burgum Bēowulf Scyldinga, lēof lēod-cyning, longe þrāge folcum gefrǣge (fæder ellor hwearf, aldor of earde), oð þæt him eft onwōc hēah Healfdene; hēold þenden lifde, gamol and gūð-rēow, glæde Scyldingas. Þǣm fēower bearn forð-gerīmed in worold wōcun, weoroda rǣswan, Heorogār and Hrōðgār and Hālga til; hȳrde ic, þat Elan cwēn Ongenþēowes wæs Heaðoscilfinges heals-gebedde. Þā wæs Hrōðgāre here-spēd gyfen, wīges weorð-mynd, þæt him his wine-māgas georne hȳrdon, oð þæt sēo geogoð gewēox, mago-driht micel. Him on mōd bearn, þæt heal-reced hātan wolde, medo-ærn micel men gewyrcean, þone yldo bearn ǣfre gefrūnon, and þǣr on innan eall gedǣlan geongum and ealdum, swylc him god sealde, būton folc-scare and feorum gumena. Þā ic wīde gefrægn weorc gebannan manigre mǣgðe geond þisne middan-geard, folc-stede frætwan. Him on fyrste gelomp ǣdre mid yldum, þæt hit wearð eal gearo, heal-ærna mǣst; scōp him Heort naman, sē þe his wordes geweald wīde hæfde. Hē bēot ne ālēh, bēagas dǣlde, sinc æt symle. Sele hlīfade hēah and horn-gēap: heaðo-wylma bād, lāðan līges; ne wæs hit lenge þā gēn þæt se ecg-hete āðum-swerian 85 æfter wæl-nīðe wæcnan scolde. Þā se ellen-gǣst earfoðlīce þrāge geþolode, sē þe in þȳstrum bād, þæt hē dōgora gehwām drēam gehȳrde hlūdne in healle; þǣr wæs hearpan swēg, swutol sang scopes. Sægde sē þe cūðe frum-sceaft fīra feorran reccan",
		    "author": <AUTHOR OBJECT>,
		    # categories this post fits into (a list of strings)
		    "categories":["web","tutorial"],
		    # comments about the post
		    "comments":[
		      {
		        "author": <AUTHOR OBJECT>,
		         "comment":"Sick Olde English"
		         "pubDate":"Fri Jan 3 15:50:40 MST 2014",
		         "guid":"5471fe89-7697-4625-a06e-b3ad18577b72"
		      }
		    ]
		    # when published
		    "pubDate":"Fri Jan 1 12:12:12 MST 2014",
		    # ID of the post (uuid or sha1)
		    "guid":"108ded43-8520-4035-a262-547454d32022"
		    # visibility ["PUBLIC","FOAF","FRIENDS","PRIVATE","SERVERONLY"]
		    "visibility":"PUBLIC"
		    # for visibility PUBLIC means it is open to the wild web
		    # FOAF means it is only visible to Friends of A Friend
		    # If any of my friends are your friends I can see the post
		    # FRIENDS means if we're direct friends I can see the post
		    # PRIVATE means only you can see the post
		    # SERVERONLY means only those on your server (your home server) can see the post
		  }
        ]  
      }
```      

### Options

In addition to the specified query parameters of the methods below, the following options are optional.

- `pageSize=<number>` A maximum of `<number>` results will be returned.
- `page=<number>` When used with `pageSize` will return the page number `<number>` of `pageSize`.

## API Methods

### Get all posts visible to the currently authenticated user

Returns all posts visible to the currently authenticated user.

##### Request:

    GET /posts
    
##### Response:

An array of post objects in chronological order.

    [
      <POST OBJECT>,
      ...
    ]
    
### Get all posts marked as public on the server

Returns all posts marked as public on the server

##### Request:

    GET /posts/public
    
##### Response:

An array of post objects in chronological order.

    [
      <POST OBJECT>,
      ...
    ]    

### Get all posts by a specific author visible to the currently authenticated user 

Returns all posts by passed author that the requesting author is authorized to view.

##### Request:

    GET /author/<AUTHOR_ID>/posts
    
##### Response:

An array of post objects in chronological order.

    [
      <POST OBJECT>,
      ...
    ]

### Get a specific single post

Returns a single post with passed ID.

##### Request:

    GET /posts/<POST_ID>

##### Response:

A single post object.

    <POST OBJECT>

### Add a comment to a post

Add the post body contents as a comment to the specified post

##### Request:

    POST /posts/<POST_ID>/comment
    
    Comment Body
    
##### Response:

The response will be HTTP status code `201 Created` on success.    

### Get all authors on host

Returns all authors on the host.

##### Request:

    GET /friends
    
##### Response:

An array of author objects in alphabetical order of display name.

    [
      <AUTHOR OBJECT>
      ...
    ]

### Get information and connections about one author on host

Returns author information and connections for given author.

##### Request:

    GET /friends/<AUTHOR_ID>

##### Response:

An object, containing an array of all connections in alphabetical order by host then username.

    {
      "id": <AUTHOR_ID>,
      "host": "hostname1",
      "displayname": "ben"
      "github": "tdubois",
      "connections": [
        <AUTHOR OBJECT>,
        ...
      ]
    }

### Query whether one author is following another.

Returns a YES or NO response whether the passed first author is following the second.

##### Request:

    GET /friends/<AUTHOR_ID1>/<AUTHOR_ID2>

##### Response:

An object, specifying the query and response.

    {
      "query": "friends",
      "authors": [
        <AUTHOR_ID1>,
        <AUTHOR_ID2>
      ],
      # or NO
      "friends": "YES" 
    }

### Query which members of a list of authors are following a specified author.

Returns a subset of the passed list of authors that are being followed by the specified author.

##### Request:

    POST /friends/<AUTHOR_ID>
    
    {
      "query": "friends",
      "author": <AUTHOR_ID>,
      "authors": [
        <AUTHOR_ID1>,
        <AUTHOR_ID2>,
        ...
      ]
    }
    
##### Response:

An object specifying the members of the passed list which are following the specified author.
   
    {
      "query": "friends",
      "author": <AUTHOR_ID>,
      "authors": [
        <AUTHOR_ID2>,
        <AUTHOR_ID5>,
        ...
      ]
    }

### Query which authors are following a specified author.

Returns all authors on host who are following a specific author.

##### Request:

    GET /friends/following/<AUTHOR_ID>
    
##### Response:

An object specifying the authors which are following the specified author.

    {
      "query": "friends",
      "author": <AUTHOR_ID>,
      "authors": [
        <AUTHOR_ID2>,
        <AUTHOR_ID5>,
        ...
      ]
    }
    
