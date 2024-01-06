
function addComment(bookId){
    let content = document.getElementById('commentId')
    if (content !== null){
        fetch('/api/comments', {
            method:'post',
            body: JSON.stringify({
                'book_id':bookId,
                'content': content.value
            }),
            headers:{
                'Content-Type':'application/json'
            }
        }).then(function (res){

            return res.json()
        }).then(function (data) {

            if(data.status == 201){
                let comments = document.getElementById('commentArea')
                comments.innerHTML=getCommentHtml(data.comment)+comments.innerHTML
            }
            else if (data.status == 404){alert(data.err_msg)}
        })
    }
}

function loadComments(bookId, page=1){
    fetch(`/api/book/${bookId}/comments?page=${page}`).then(res=>res.json()).then(data=>{
        console.info(data)
        let comments = document.getElementById('commentArea')
        comments.innerHTML=""
        for(let i=0; i<data.length;i++)
            comments.innerHTML+=getCommentHtml(data[i])
    })
}

function getCommentHtml(comment){
    let image = comment.user.avatar
    if (image===null || !image.startsWith('https'))
        image='https://hanoispiritofplace.com/wp-content/uploads/2017/05/tai-anh-tinh-yeu-dep-5.jpg'
    return`
    <div class="row" 
        style=" margin: 5px 0"
       
        
        
        >
            <div class="col-md-1 col-xs-4">
                    <img class="rounded-circle img-fluid" alt="demo" src="${image}"/>
            </div>

            <div class="col-md-11 col-xs-8" style="">
                <p>${ comment.content }</p>
                <p><em>${moment(comment.created_date).locale('vi').fromNow() }</em></p>
            </div>
            <hr/>
     </div>
    `
}