from django.db import transaction
from django.http import JsonResponse, Http404
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from systemconfig.models import Settings
from systemconfig.selectors import settings_get
from systemconfig.services.settings_services import settings_update


class SettingsDetailApi(APIView):
    permission_classes = [AllowAny]

    class OutputSerializer(serializers.Serializer):
        id = serializers.CharField(required=True)
        options = serializers.JSONField(required=True)

    def get(self, request):
        settings = Settings.objects.first()

        if settings is None:
            raise Http404

        data = self.OutputSerializer(settings).data

        return Response(data)


class SettingsUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        options = serializers.JSONField(required=True)

    @transaction.atomic
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        settings = settings_get(settings_id=1)

        if settings is None:
            raise Http404

        settings = settings_update(settings=settings, data=serializer.validated_data)

        # Note: This shows a possible reusability for serializers between APIs
        # Usually, this is how we approach things, when building APIs at first
        # But at the very moment when we need to make a change to the output,
        # that's specific to this API, we'll introduce a separate OutputSerializer just for this API
        data = self.InputSerializer(settings).data

        return Response(data)


def get_settings(request):
    settings_obj = {
        "id": 1,
        "options": {
            "deliveryTime": [
                {
                    "title": "Express Delivery",
                    "description": "90 min express delivery"
                },
                {
                    "title": "Morning",
                    "description": "8.00 AM - 11.00 AM"
                },
                {
                    "title": "Noon",
                    "description": "11.00 AM - 2.00 PM"
                },
                {
                    "title": "Afternoon",
                    "description": "2.00 PM - 5.00 PM"
                },
                {
                    "title": "Evening",
                    "description": "5.00 PM - 8.00 PM"
                }
            ],
            "isProductReview": False,
            "useGoogleMap": False,
            "enableTerms": True,
            "enableCoupons": True,
            "enableReviewPopup": True,
            "reviewSystem": {
                "value": "review_single_time",
                "name": "Give purchased product a review only for one time. (By default)"
            },
            "seo": {
                "ogImage": None,
                "ogTitle": None,
                "metaTags": None,
                "metaTitle": None,
                "canonicalUrl": None,
                "ogDescription": None,
                "twitterHandle": None,
                "metaDescription": None,
                "twitterCardType": None
            },
            "logo": {
                "thumbnail": "https://pickbazarlaravel.s3.ap-southeast-1.amazonaws.com/2295/conversions/Logo-new-thumbnail.jpg",
                "original": "https://pickbazarlaravel.s3.ap-southeast-1.amazonaws.com/2295/Logo-new.png",
                "id": 2298,
                "file_name": "Logo-new.png"
            },
            "collapseLogo": {
                "thumbnail": "https://pickbazarlaravel.s3.ap-southeast-1.amazonaws.com/2283/conversions/Pickbazar-thumbnail.jpg",
                "original": "https://pickbazarlaravel.s3.ap-southeast-1.amazonaws.com/2283/Pickbazar.png",
                "id": 2286,
                "file_name": "Pickbazar.png"
            },
            "useOtp": False,
            "currency": "USD",
            "taxClass": "1",
            "siteTitle": "Hotels",
            "freeShipping": False,
            "signupPoints": 100,
            "siteSubtitle": "Your next ecommerce",
            "shippingClass": "1",
            "contactDetails": {
                "contact": "+129290122122",
                "socials": [
                    {
                        "url": "https://www.facebook.com/redqinc",
                        "icon": "FacebookIcon"
                    },
                    {
                        "url": "https://twitter.com/RedqTeam",
                        "icon": "TwitterIcon"
                    },
                    {
                        "url": "https://www.instagram.com/redqteam",
                        "icon": "InstagramIcon"
                    }
                ],
                "website": "https://redq.io",
                "emailAddress": "demo@demo.com",
                "location": {
                    "lat": 42.9585979,
                    "lng": -76.9087202,
                    "zip": None,
                    "city": None,
                    "state": "NY",
                    "country": "United States",
                    "formattedAddress": "NY State Thruway, New York, USA"
                }
            },
            "paymentGateway": [
                {
                    "name": "stripe",
                    "title": "Stripe"
                }
            ],
            "currencyOptions": {
                "formation": "en-US",
                "fractions": 2
            },
            "useEnableGateway": False,
            "useCashOnDelivery": True,
            "freeShippingAmount": 0,
            "minimumOrderAmount": 0,
            "useMustVerifyEmail": False,
            "maximumQuestionLimit": 5,
            "currencyToWalletRatio": 3,
            "StripeCardOnly": False,
            "guestCheckout": True,
            "server_info": {
                "upload_max_filesize": 2048,
                "memory_limit": "128M",
                "max_execution_time": "30",
                "max_input_time": "-1",
                "post_max_size": 8192
            },
            "useAi": False,
            "defaultAi": "openai",
            "maxShopDistance": None,
            "siteLink": "https://pickbazar.redq.io",
            "copyrightText": "Copyright \u00a9 REDQ. All rights reserved worldwide.",
            "externalText": "REDQ",
            "externalLink": "https://redq.io",
            "smsEvent": {
                "admin": {
                    "statusChangeOrder": False,
                    "refundOrder": False,
                    "paymentOrder": False
                },
                "vendor": {
                    "statusChangeOrder": False,
                    "paymentOrder": False,
                    "refundOrder": False
                },
                "customer": {
                    "statusChangeOrder": False,
                    "refundOrder": False,
                    "paymentOrder": False
                }
            },
            "emailEvent": {
                "admin": {
                    "statusChangeOrder": False,
                    "refundOrder": False,
                    "paymentOrder": False
                },
                "vendor": {
                    "createQuestion": False,
                    "statusChangeOrder": False,
                    "refundOrder": False,
                    "paymentOrder": False,
                    "createReview": False
                },
                "customer": {
                    "statusChangeOrder": False,
                    "refundOrder": False,
                    "paymentOrder": False,
                    "answerQuestion": False
                }
            },
            "pushNotification": {
                "all": {
                    "order": False,
                    "message": False,
                    "storeNotice": False
                }
            },
            "isUnderMaintenance": False,
            "maintenance": {
                "title": "Site is under Maintenance",
                "buttonTitleOne": "Notify Me",
                "newsLetterTitle": "Subscribe Newsletter",
                "buttonTitleTwo": "Contact Us",
                "contactUsTitle": "Contact Us",
                "aboutUsTitle": "About Us",
                "isOverlayColor": False,
                "overlayColor": None,
                "overlayColorRange": None,
                "description": "We are currently undergoing essential maintenance to elevate your browsing experience. Our team is working diligently to implement improvements that will bring you an even more seamless and enjoyable interaction with our site. During this period, you may experience temporary inconveniences. We appreciate your patience and understanding. Thank you for being a part of our community, and we look forward to unveiling the enhanced features and content soon.",
                "newsLetterDescription": "Stay in the loop! Subscribe to our newsletter for exclusive deals and the latest trends delivered straight to your inbox. Elevate your shopping experience with insider access.",
                "aboutUsDescription": "Welcome to Pickbazar, your go-to destination for curated excellence. Discover a fusion of style, quality, and affordability in every click. Join our community and elevate your shopping experience with us!",
                "image": {
                    "id": 1794,
                    "file_name": "background.png",
                    "original": "https://pickbazarlaravel.s3.ap-southeast-1.amazonaws.com/1792/background.png",
                    "thumbnail": "https://pickbazarlaravel.s3.ap-southeast-1.amazonaws.com/1792/conversions/background-thumbnail.jpg"
                },
                "start": "2024-01-31T06:33:30.201258Z",
                "until": "2024-02-01T06:33:30.201274Z"
            },
            "isPromoPopUp": True,
            "promoPopup": {
                "image": {
                    "id": 1793,
                    "original": "https://pickbazarlaravel.s3.ap-southeast-1.amazonaws.com/1791/pickbazar02.png",
                    "file_name": "pickbazar02.png",
                    "thumbnail": "https://pickbazarlaravel.s3.ap-southeast-1.amazonaws.com/1791/conversions/pickbazar02-thumbnail.jpg"
                },
                "title": "Get 25% Discount",
                "popUpDelay": 5000,
                "description": "Subscribe to the mailing list to receive updates on new arrivals, special offers and our promotions.",
                "popUpNotShow": {
                    "title": "Don't show this popup again",
                    "popUpExpiredIn": 7
                },
                "isPopUpNotShow": True,
                "popUpExpiredIn": 1
            },
            "app_settings": {
                "last_checking_time": "2024-02-06T06:07:32.543238Z",
                "trust": True
            }
        },
        "language": "en",
        "created_at": "2024-01-31T06:33:30.000000Z",
        "updated_at": "2024-02-06T06:07:32.000000Z"
    }
    return JsonResponse(settings_obj)
