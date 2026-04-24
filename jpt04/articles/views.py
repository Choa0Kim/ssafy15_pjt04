import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from django.conf import settings
from django.contrib import messages
from .models import Post
from .utils import is_inappropriate

def load_assets():
    file_path = os.path.join(settings.BASE_DIR, 'data', 'assets.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_smart_money():
    file_path = os.path.join(settings.BASE_DIR, 'data', 'smart_money.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def index(request):
    assets = load_assets()
    return render(request, 'articles/index.html', {'assets': assets})

def portfolio(request):
    smart_money_data = load_smart_money()
    # 기본값으로 워런 버핏의 댓글을 가져옴 (초기 렌더링용)
    initial_portfolio_id = "warren_buffett"
    comments = Post.objects.filter(asset_id=initial_portfolio_id).order_by('-created_at')
    
    context = {
        'smart_money': json.dumps(smart_money_data),
        'initial_comments': comments,
        'metadata': smart_money_data.get('metadata', {})
    }
    return render(request, 'articles/portfolio.html', context)

def portfolio_comment(request, portfolio_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        author = request.POST.get('author') or "익명"
        
        if content:
            if is_inappropriate("Portfolio Comment", content):
                return JsonResponse({'status': 'error', 'message': '부적절한 내용이 포함되어 있습니다.'}, status=400)
            
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

def asset_board(request, asset_id):
    assets = load_assets()
    asset = next((a for a in assets if a['id'] == asset_id), None)
    if not asset:
        raise Http404("존재하지 않는 자산입니다.")
    
    posts = Post.objects.filter(asset_id=asset_id).order_by('-created_at')
    context = {
        'asset': asset,
        'posts': posts,
    }
    return render(request, 'articles/asset_board.html', context)

def post_create(request, asset_id):
    assets = load_assets()
    asset = next((a for a in assets if a['id'] == asset_id), None)
    if not asset:
        raise Http404("존재하지 않는 자산입니다.")

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.POST.get('author') or "익명"
        
        if title and content:
            if is_inappropriate(title, content):
                messages.error(request, "부적절한 내용이 포함되어 있습니다. 수정 후 다시 등록해 주세요.")
                return render(request, 'articles/post_create.html', {
                    'asset': asset,
                    'title': title,
                    'content': content,
                    'author': author
                })
            
            Post.objects.create(asset_id=asset_id, title=title, content=content, author=author)
            return redirect('articles:asset_board', asset_id=asset_id)
            
    return render(request, 'articles/post_create.html', {'asset': asset})

def post_detail(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    assets = load_assets()
    asset = next((a for a in assets if a['id'] == post.asset_id), None)
    if not asset:
        raise Http404("게시글과 연결된 자산 정보를 찾을 수 없습니다.")
    return render(request, 'articles/post_detail.html', {'post': post, 'asset': asset})

def post_update(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    assets = load_assets()
    asset = next((a for a in assets if a['id'] == post.asset_id), None)
    if not asset:
        raise Http404("게시글과 연결된 자산 정보를 찾을 수 없습니다.")
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.POST.get('author') or "익명"
        if title and content:
            if is_inappropriate(title, content):
                messages.error(request, "부적절한 내용이 포함되어 있습니다. 수정 후 다시 등록해 주세요.")
                return render(request, 'articles/post_update.html', {
                    'post': post, 'asset': asset, 'error_title': title, 'error_content': content, 'error_author': author
                })
            post.title = title
            post.content = content
            post.author = author
            post.save()
            return redirect('articles:post_detail', post_pk=post.pk)
    return render(request, 'articles/post_update.html', {'post': post, 'asset': asset})

def post_delete(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    asset_id = post.asset_id
    if request.method == 'POST':
        post.delete()
        return redirect('articles:asset_board', asset_id=asset_id)
    return redirect('articles:post_detail', post_pk=post.pk)
