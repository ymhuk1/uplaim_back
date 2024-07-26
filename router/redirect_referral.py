from typing import Optional, Annotated, Union

from fastapi import APIRouter, Query, Header
from starlette.responses import RedirectResponse, HTMLResponse

redirect_router = APIRouter(
    prefix="/referral",
    tags=["Редирект"],
)


@redirect_router.get("")
async def redirect_referral(referral: Optional[str] = Query(None, alias="referral"),
                            user_agent: Annotated[Union[str, None], Header()] = None):
    if referral:
        ios_app_url = f'uplaim://app?referral={referral}'
        android_app_url = f'intent://app?referral={referral}#Intent;scheme=uplaim;package=com.viktorka.uplaim;end'

        ios_store_url = 'https://apps.apple.com'
        android_store_url = 'https://play.google.com'

        if 'iPhone' in user_agent or 'iPad' in user_agent:
            fallback_html = f"""
                <html>
                <head>
                    <title>Redirecting...</title>
                    <meta http-equiv="refresh" content="0;url={ios_app_url}">
                    <script type="text/javascript">
                        setTimeout(function() {{
                            window.location.href = "{ios_store_url}";
                        }}, 1500);
                    </script>
                </head>
                <body>
                    <p>If you are not redirected automatically, follow this <a href="{ios_store_url}">link</a>.</p>
                </body>
                </html>
                """
            return HTMLResponse(content=fallback_html)
        elif 'Android' in user_agent:
            fallback_html = f"""
                <html>
                <head>
                    <title>Redirecting...</title>
                    <meta http-equiv="refresh" content="0;url={android_app_url}">
                    <script type="text/javascript">
                        setTimeout(function() {{
                            window.location.href = "{android_store_url}";
                        }}, 1500);
                    </script>
                </head>
                <body>
                    <p>If you are not redirected automatically, follow this <a href="{android_store_url}">link</a>.</p>
                </body>
                </html>
                """
            return HTMLResponse(content=fallback_html)
        else:
            return RedirectResponse(url='https://uplaim.com')
    if referral is None:
        return None

