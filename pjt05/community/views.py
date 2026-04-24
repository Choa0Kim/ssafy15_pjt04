from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .utils import load_assets, get_asset_by_id
from .models import Post, Comment
from .forms import CommentForm
from .llm import is_inappropriate


from django.http import JsonResponse
import json

def asset_list(request):
    """금융 자산 리스트 및 포트폴리오 메인 (JSON에서 로드)"""
    from .utils import load_smart_money
    assets = load_assets()
    smart_money_data = load_smart_money()
    
    # 기본 포트폴리오(워런 버핏)의 초기 댓글 로드
    initial_portfolio_id = "warren_buffett"
    comments = Post.objects.filter(asset_id=initial_portfolio_id).order_by('-created_at')
    
    context = {
        "assets": assets,
        "smart_money": json.dumps(smart_money_data),
        "initial_comments": comments,
        "metadata": smart_money_data.get('metadata', {})
    }
    return render(request, "community/asset_list.html", context)

@login_required
@require_http_methods(["POST"])
def portfolio_comment(request, portfolio_id):
    content = request.POST.get('content')
    author = request.user.username
    
    if content:
        if is_inappropriate(content):
            return JsonResponse({'status': 'error', 'message': '부적절한 단어가 포함되어 있습니다.'}, status=400)
        
        post = Post.objects.create(
            asset_id=portfolio_id,
            title=f"Comment on {portfolio_id}",
            content=content,
            author=author
        )
        return JsonResponse({
            'status': 'success',
            'author': post.author,
            'content': post.content,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'status': 'error', 'message': '잘못된 요청입니다.'}, status=400)

def get_portfolio_comments(request, portfolio_id):
    comments = Post.objects.filter(asset_id=portfolio_id).order_by('-created_at')
    data = [{
        'author': c.author,
        'content': c.content,
        'created_at': c.created_at.strftime('%Y-%m-%d %H:%M')
    } for c in comments]
    return JsonResponse({'comments': data})


def board(request, asset_id):
    """해당 자산의 토론 게시판 (게시글 목록)"""
    asset = get_asset_by_id(asset_id)
    if not asset:
        return render(request, "community/404.html", status=404)
    posts = Post.objects.filter(asset_id=asset_id)
    context = {"asset": asset, "posts": posts}
    return render(request, "community/board.html", context)


def post_detail(request, asset_id, post_id):
    """게시글 상세"""
    asset = get_asset_by_id(asset_id)
    if not asset:
        return render(request, "community/404.html", status=404)
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    comments = post.comments.all()
    comment_form = CommentForm()
    
    context = {
        "asset": asset, 
        "post": post,
        "comments": comments,
        "comment_form": comment_form
    }
    return render(request, "community/post_detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def post_create(request, asset_id):
    """게시글 작성"""
    asset = get_asset_by_id(asset_id)

    if not asset:
        return render(request, "community/404.html", status=404)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        author = request.user.username

        if title and content:
            if is_inappropriate(title + " " + content):
                messages.error(request, "부적절한 단어가 포함되어 있어 게시글을 등록할 수 없습니다.")
                return render(request, "community/post_form.html", {"asset": asset, "title": title, "content": content})

            Post.objects.create(
                asset_id=asset_id,
                title=title,
                content=content,
                author=author,
            )
            return redirect("community:board", asset_id=asset_id)
    context = {"asset": asset}
    return render(request, "community/post_form.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def post_update(request, asset_id, post_id):
    """게시글 수정"""
    asset = get_asset_by_id(asset_id)

    if not asset:
        return render(request, "community/404.html", status=404)
        
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)

    if post.author != request.user.username:
        messages.error(request, "수정 권한이 없습니다.")
        return redirect("community:post_detail", asset_id=asset_id, post_id=post.id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        
        if title and content:
            if is_inappropriate(title + " " + content):
                messages.error(request, "부적절한 단어가 포함되어 있어 수정할 수 없습니다.")
            else:
                post.title = title
                post.content = content
                post.save()
                return redirect("community:post_detail", asset_id=asset_id, post_id=post.id)

    context = {
        "asset": asset,
        "post": post,
        "title": request.POST.get("title", post.title) if request.method == "POST" else post.title,
        "content": request.POST.get("content", post.content) if request.method == "POST" else post.content,
        "author": post.author,
        "is_edit": True,
    }
    return render(request, "community/post_form.html", context)


@login_required
@require_http_methods(["POST"])
def post_delete(request, asset_id, post_id):
    """게시글 삭제"""
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    
    if post.author != request.user.username:
        messages.error(request, "삭제 권한이 없습니다.")
        return redirect("community:post_detail", asset_id=asset_id, post_id=post.id)

    post.delete()
    messages.success(request, "게시글이 삭제되었습니다.")
    return redirect("community:board", asset_id=asset_id)


@login_required
@require_http_methods(["POST"])
def comment_create(request, asset_id, post_id):
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        content = form.cleaned_data['content']
        if is_inappropriate(content):
            messages.error(request, "부적절한 단어가 포함되어 있어 댓글을 등록할 수 없습니다.")
        else:
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user.username
            comment.save()
    return redirect('community:post_detail', asset_id=asset_id, post_id=post.id)


@login_required
@require_http_methods(["POST"])
def comment_delete(request, asset_id, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    comment = get_object_or_404(Comment, id=comment_id, post=post)
    if comment.author == request.user.username:
        comment.delete()
    else:
        messages.error(request, "삭제 권한이 없습니다.")
    return redirect('community:post_detail', asset_id=asset_id, post_id=post.id)
