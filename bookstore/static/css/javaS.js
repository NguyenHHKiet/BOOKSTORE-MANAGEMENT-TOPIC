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
                content.value=''
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
    <div class="content-section">
        <div class="d-flex">
            <div class="w-100">
                <img class="rounded-circle account-img"
                    style="
                        width: 30px;
                        height: 30px;
                        margin: 0px 10px 0px 0;
                    "
                    src="${image}"/>
                <span class="text-muted">${ comment.user.username }</span>
            </div>
            <p class="flex-shrink-1 text-nowrap text-success"><em>${moment(comment.created_date).locale('en').fromNow() }</em></p>
        </div>

        <div class="bg-white rounded p-2 mt-1 border border-1" style="">
            ${ comment.content }
        </div>
    </div>
    `
}