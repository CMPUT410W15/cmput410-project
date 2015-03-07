# SocialDistribution API Doc

## Contents

### Friends

- Get all authors on host.
- Get information and connections about one author on host.
- Get the authors on the host following a speicific author on a specific host.

### Posts

 - Get all posts by an author.
 - Get all comments on a post.
 - Add a comment to a post.
 
## API Requirements

### Endpoint

All URIs in this document are located at the endpoint: `http://cs410.cs.ualberta.ca:41081/api/`. 

All requests must make use of HTTP Basic Auth using a username and password negotiated at time of server setup.

### RSA Keys

To create a connection between two hosts, both hosts will be required to share the public key portion of an RSA key pair that is unique to that host.

This allows for encrypted communication, and confidence in the source of communication.

### Objects

- **Author:** An author is the user entity on the host.  An author is associated with one host and has a username that is unique on that host.
- **Connection:** An author has 0 or more connections with other authors. A connections is a one-way relationship indicating that the connecting author *"follows"* the connected author. When two authors *"follow"* each other, they are said to be *"friends"*.
- **Post:** Authors create posts which contain optionally a text body and image.
- **Comment:** A comment is created by and author and associated with a post. It has a text body.

### Options

In addition to the specified query parameters of the methods below, the following options are optional.

- `pageSize=<number>` A maximum of `<number>` results will be returned.
- `page=<number>` When used with `pageSize` will return the page number `<number>` of `pageSize`.

## API Methods

### Get all authors on host

Returns all authors on the host.

##### Request:

    GET /authors
    
##### Response:

An array of author names in alphabetical order.


    [
      "username": "Ben",
      ...
    ]

### Get information and connections about one author on host

Returns author information and connections for given author.

##### Request:

    GET /author/Ben

##### Response:

An author object, containing an array of all connections in alphabetical order by host then username.

    {
      "host": "hostname1",
      "github": "tdubois",
      "connections": [
      	{ 
          "host": "hostname1",
          "username": "konrad"
        },
        {
          "host": "hostname2",
          "username": "neil"
        },
        ...
      ]
    }

### Get the authors on the host following a speicific author on a specific host

Returns all authors on host who are following a specific author on a specific host.

##### Request:

    GET /authors/following/?author="ben"&host="hostname1"
    
##### Response:

An array of author names in alphabetical order.

    [
      "username": "Ben",
      ...
    ]
    
### Get all posts by an author 

Returns all posts by passed author that the requesting author is authorized to view.

##### Request:

    GET /posts/ben/?author="konrad"&host="hostname1"
    
##### Response:

An array of post objects that the requesting user is authorized to view in chronological order.

    [
      {
        "id": "unique id",
        "title": "title",
        "content": "content",
        "content_type": "plaintext OR markdown",
        "author": "ben",
        "published": 12475896,
        "image": "URL"        
      },
      ...
    ]

### Get all comments on a post

Returns all comments on a given post.

##### Request:

    GET /posts/id/comment
    
##### Response:

An array of comment objects in chronological order.

    [
      {
        "content": "content",
        "author": "ben",
        "published": 12527889
      },
      ...
    ]