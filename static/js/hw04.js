const story2Html = story => {
    return `
        <div>
            <img src="${ story.user.thumb_url }" class="pic" alt="profile pic for ${ story.user.username }" />
            <p>${ story.user.username }</p>
        </div>
    `;
};

const stringToHTML = htmlString => {
    var parser = new DOMParser();
    var doc = parser.parseFromString(htmlString, 'text/html');
    return doc.body.firstChild;
};

const redrawPost = (postId, callback) => {
    // first, requiry the API for the post that has just been changed 
    fetch(`/api/posts/${postId}`)
    .then(response => response.json())
    // .then(updatedPost =>  {
    //     console.log(updatedPost);
    //     const html = post2Html(updatedPost);
    //     const newElement = stringToHTML(html);
    //     const postElement = document.querySelector(`#post_${postId}`);
    //     postElement.innerHTML = newElement.innerHTML;
    //     // then, after you get the response, redraw the post
    // })
    .then(updatedPost => {
        if (!callback) {
            redrawCard(updatedPost);
       
        } else {
            callback(updatedPost);
        }
    });
};

const redrawCard = post => {
    console.log(post);
    const html = post2Html(post);
    const newElement = stringToHTML(html);
    const postElement = document.querySelector(`#post_${post.id}`);
    console.log(newElement.innerHTML);
    postElement.innerHTML = newElement.innerHTML;
};

const displayComments = post => {
    if (post.comments.length > 1) {
        // display button
        return `
        <p>
            <button 
                data-post-id=${post.id} 
                onclick="showModal(event);" 
                class="comment-button"
                id="activate-default">
                View all ${post.comments.length} comments</button>
        </p>
        <p class="comments"><strong>${post.comments[post.comments.length - 1].user.username}</strong>&nbsp&nbsp${post.comments[post.comments.length - 1].text}</p>
        <p id="time">${post.comments[post.comments.length - 1].display_time}</p>
        `;
    
    } else if (post.comments.length === 1){
        // display single comment
        return `
        <p class="comments"><strong>${post.comments[0].user.username}</strong>&nbsp&nbsp${post.comments[0].text}</p>
        <p id="time">${post.comments[0].display_time}</p>
        `;
    
    } else {
        return '';
    }
};

const displayAllComments = post => {
    let html = ``;

    html += `                       
    <span style="display: flex; align-item: flex-start; padding-bottom: 25px;">
        <img id="postProfile" src="${post.user.thumb_url}" alt="profile photo for ${post.user.username}">
        <h1 style="margin-left: 15px;"><strong>${post.user.username}</strong></h1>
    </span>
    `

    for (let i = 0; i < post.comments.length; i++) {
        html += `
        <div >
        <span class="modal-stack" style="display: flex;">

            <img class="modalpic" style="width: 30px; height: 30px; border-radius: 15px;" 
            src="${post.comments[i].user.thumb_url}"/>
 
           
            <span style="display: flex; flex-direction: column; padding-top: 0px; flex-grow: 2;">
                <p class="comments" id="modal_p" style="margin-top: 0px; "><strong>${post.comments[i].user.username}<strong>&nbsp&nbsp<strong style="font-weight: normal;">${post.comments[i].text}</strong></p>
                <p id="time" style="padding-top: 0px;"><b>${post.comments[i].display_time}<b></p>
            </span>
            
            <button><i class="far fa-heart"></i></button>
        </span>
        </div>
        `
    }
    return html;
};

const addComment = (postID, input, ev) => { 
    console.log("Add Comment...");
    console.log(ev);
    
    const postData = {
        "post_id": postID,
        "text": input
    };
    console.log(postID);
    console.log(input)

    fetch("/api/comments/", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => {
        response.json()
        if (response.status === 201) {
            displayPosts();
        }
    })
};

const showModal = ev => {
    const postId = Number(ev.currentTarget.dataset.postId)
    const modalElement = document.querySelector('.modal-bg');
    
    redrawPost(postId, post => {
        const html = post2Modal(post);
        document.querySelector(`#post_${post.id}`).insertAdjacentHTML('beforeend', html);
        modalElement.classList.remove('hidden');
        modalElement.setAttribute('aria-hidden', 'false');
        document.querySelector('body').style.overflowY = "hidden";
        document.querySelector('.close').focus();
    });
};

const closeModal = ev => {
    console.log("close modal");
    const modalElement = document.querySelector('.modal-bg');

    document.querySelector('.modal-bg').remove();
    document.querySelector('body').style.overflowY = "auto";
    document.querySelector('.comment-button').focus();
    modalElement.setAttribute('aria-hidden', 'true');
};

// Tabbing in modal only
document.addEventListener('focus', function(event) {
    const modalElement = document.querySelector('.modal-bg');
    console.log('focus');
    if (modalElement.getAttribute('aria-hidden') === 'false' && !modalElement.contains(event.target)) {
        console.log('back to top!');
        event.stopPropagation();
        document.querySelector('.close').focus();
    }
}, true);

// Escape Key
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closeModal();
    }
  })

const post2Modal = post => {
    return `
    <div id="dialog" class="modal-bg hidden" aria-hidden="true" role="dialog">
        <section class="modal">
            <button class="close" 
                aria-label="Close the modal window"
                onclick="closeModal(event);"
                id="close-button">
                    Close
            </button>
            
            <div class="modal-body">
                <span id="modal-comments">
                    <img id="modal_post" src="${post.image_url}"/>
                
                    <div id="all-comments">
                        ${displayAllComments(post)}
                    </div>
                <span>
            </div>
        </section>
    </div>
    `;
};

const post2Html = post => {
    return `
        <section id="post_${post.id}" style="border: solid #e5e5e5;">
            <h3 style="color=#444;">${post.user.username}</h3>

            <img style="width: 100%;" src="${post.image_url}" alt="${post.user.username}'s post"/>

            <span class="icons">
            <span>
                ${renderLikeButton(post)}
                <button>
                    <i class="far fa-comment"></i>
                </button>
                <button>
                    <i class="far fa-paper-plane"></i>
                </button>
            </span>
            
            <span>
                ${renderBookmarkButton(post)}
            </span>
            </span>

            <div id="likes" style="padding-top: 0px;">
                <b>${post.likes.length} like${(post.likes.length == 1) | (post.likes.length == 0)? '' : 's'}</b>
            </div>
            
            <p><strong>${post.user.username}</strong>&nbsp&nbsp${post.caption}</p>
            
            <p id="time">
                ${post.display_time}
            </p>

            ${displayComments(post)}

            <hr style="width:100%; height:2px; text-align:left; margin-left:0px; border-top:2px solid #e5e5e5"/>
            
            <span class="add-comment" style="display: flex; justify-content: space-between;">
                <input type="text" 
                    placeholder="Add a comment..." class="add-comment" id="comment-${post.id}" class="input-holder" 
                    style="color: #999; border: none; font-size: 20px;">
                
                <button 
                    style="color: rgb(44, 105, 155); padding-right: 20px;"
                    onclick="addComment(${post.id}, document.getElementById('comment-${post.id}').value, event);"
                    class="postComment">
                    Post
                </button>
            </span>
        </section>

        <hr style="width:100%; height:10px; text-align:left; margin-left:0px; border-top:10px solid #f2f2f2"/>
    `;
};

const handleLike = ev => {
    const elem = ev.currentTarget;

    // if aria-checked === 'true' -> delete the like object (unlike)
    // else -> issue a post to create a like object
    
    if (elem.getAttribute('aria-checked') === 'true') {
        unlikePost(elem);
    
    } else {
        likePost(elem);
    }

    // after everything is done, you want to redraw the post to reflect
    // its new status
};

const likePost = elem => {
    console.log("like post", elem);

    const postId = Number(elem.dataset.postId);
    const postData = {
        "post_id": postId
    };
    fetch("/api/posts/likes/", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(postData)
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            console.log("redraw the post");
            redrawPost(postId);
        });
};

const unlikePost = elem => {
    console.log("unlike post", elem);

    const postId = Number(elem.dataset.postId);
    fetch(`/api/posts/likes/${elem.dataset.likeId}`, {
        method: "DELETE",
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        console.log("redraw the post");
        // here is where we redraw the post
        redrawPost(postId);
    });
};

const handleBookmark = ev =>{
    const elem = ev.currentTarget;

    if (elem.getAttribute('aria-checked') === 'true') {
        unbookmarkPost(elem);
    
    } else {
        bookmarkPost(elem);
    }
};

const bookmarkPost = elem => {
    console.log("bookmark post", elem);

    const postId = Number(elem.dataset.postId);
    const postData = {
        "post_id": postId
    };
    fetch("/api/bookmarks", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(postData)
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            console.log("redraw the post");
            redrawPost(postId);
        });
};

const unbookmarkPost = elem => {
    console.log("unbookmark post", elem);

    const postId = Number(elem.dataset.postId);
    fetch(`/api/bookmarks/${elem.dataset.bookmarkId}`, {
        method: "DELETE",
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        console.log("redraw the post");
        // here is where we redraw the post
        redrawPost(postId);
    });
};

const renderLikeButton = post => {
    if (post.current_user_like_id) {
        return `
            <button 
                data-post-id="${post.id}"
                data-like-id="${post.current_user_like_id}"
                aria-label="Like / Unlike"
                aria-checked="true"
                onclick="handleLike(event);">
                    <i class="fas fa-heart"></i>
            </button>
        `;
    } else {
        return `
            <button 
                data-post-id="${post.id}"
                aria-label="Like / Unlike"
                aria-checked="false"
                onclick="handleLike(event);">
                    <i class="far fa-heart"></i>
            </button>
        `;
    }
};

const renderBookmarkButton = post => {
    if (post.current_user_bookmark_id) {
        return `
            <button 
                data-post-id="${post.id}"
                data-bookmark-id="${post.current_user_bookmark_id}"
                aria-label="Bookmark / Unbookmark"
                aria-checked="true"
                onclick="handleBookmark(event);">
                    <i class="fas fa-bookmark"></i>
            </button>
        `;
    } else {
        return `
            <button 
                data-post-id="${post.id}"
                aria-label="Bookmark/ Unbookmark"
                aria-checked="false"
                onclick="handleBookmark(event);">
                    <i class="far fa-bookmark"></i>
            </button>
        `;
    }
};

// fetch data from your API endpoint:
const displayPosts = () => {
    fetch('/api/posts')
        .then(response => response.json())
        .then(posts => {
            console.log(posts);
            const html = posts.map(post2Html).join('\n');
            document.querySelector('#posts').innerHTML = html;
        })
};

// fetch data from your API endpoint:
const displayStories = () => {
    fetch('/api/stories')
        .then(response => response.json())
        .then(stories => {
            const html = stories.map(story2Html).join('\n');
            document.querySelector('.stories').innerHTML = html;
        })
};

const displayProfile = () => {
    fetch('/api/profile')
        .then(response => response.json())
        .then(user => {
            const html = `
                <img src="${user.image_url}" alt="profile photo for ${user.username}">
                <h1 style="margin-left: 15px;"><strong>${user.username}</strong></h1>
            `;
            document.querySelector('.profile').innerHTML = html;
        })
};

const initPage = () => {
    displayStories();
    displayPosts();
    displayProfile();
};

// invoke init page to display stories:
initPage();
