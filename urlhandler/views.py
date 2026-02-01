from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import shorturl
import base64

# ----------------------------
# Base64 helpers (URL-safe)
# ----------------------------

def encode_id(num: int) -> str:
    encoded = base64.urlsafe_b64encode(str(num).encode())
    return encoded.decode().rstrip("=")


def decode_id(encoded: str) -> int:
    padding = '=' * (-len(encoded) % 4)
    decoded = base64.urlsafe_b64decode(encoded + padding)
    return int(decoded.decode())


@login_required(login_url='/login/')
def dashboard(request):
    urls = shorturl.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'urls': urls})



@login_required(login_url='/login/')
def generate(request):
    if request.method != 'POST':
        return redirect('dashboard')

    original = request.POST.get('original')
    custom_short = request.POST.get('short')

    if not original:
        messages.error(request, "Original URL is required")
        return redirect('dashboard')

    # Custom short URL
    if custom_short:
        if shorturl.objects.filter(short_query=custom_short).exists():
            messages.error(request, "Short URL already exists")
            return redirect('dashboard')

        shorturl.objects.create(
            user=request.user,
            original_url=original,
            short_query=custom_short
        )

        messages.success(request, "Short URL created successfully")
        return redirect('dashboard')

    new_url = shorturl.objects.create(
        user=request.user,
        original_url=original,
        short_query="temp"
    )

    new_url.short_query = encode_id(new_url.id)
    new_url.save()

    messages.success(request, "Short URL generated successfully")
    return redirect('dashboard')


@login_required(login_url='/login/')
def edit_url(request, id):
    url = get_object_or_404(shorturl, id=id, user=request.user)

    if request.method == 'POST':
        new_original = request.POST.get('original')
        new_short = request.POST.get('short')

        if not new_original or not new_short:
            messages.error(request, "Original URL and Short URL cannot be empty")
            return redirect('edit', id=id)

        if shorturl.objects.filter(short_query=new_short).exclude(id=url.id).exists():
            messages.error(request, "Short URL already exists")
            return redirect('edit', id=id)

        url.original_url = new_original
        url.short_query = new_short
        url.save()

        messages.success(request, "URL updated successfully")
        return redirect('dashboard')

    return render(request, 'edit.html', {'url': url})



@login_required(login_url='/login/')
def delete_url(request, id):
    url = get_object_or_404(shorturl, id=id, user=request.user)
    url.delete()
    messages.success(request, "URL deleted successfully")
    return redirect('dashboard')



def home(request, query=None):
    if not query:
        return render(request, 'home.html')

    try:
        url = shorturl.objects.get(short_query=query)
        url.visits += 1
        url.save()
        return redirect(url.original_url)

    except shorturl.DoesNotExist:
        return render(request, 'home.html', {'error': True})
