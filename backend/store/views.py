from .models import Item, Order, OrderItem, BillingAddress
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .serializers import ItemSerializers, CartItemSerializer, Task_extendedSerializer, OrderSerializers, OrderItemSerializers, TaskSerializer, JoinTaskSerializer
from rest_framework import generics, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, authentication
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt # new
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
import stripe
from django.conf import settings #n
from django.http.response import JsonResponse #n
from django.db.models import Q

class Home(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializers
    permission_classes = (permissions.AllowAny, )

    def get_queryset(self, *args, **kwargs):
        # Start with all items
        qs = Item.objects.all()
        # Retrieve the 'category' and 'label' query parameters from the request
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        label = self.request.GET.get('label')
        # Apply filters if 'category' and 'label' are provided
        if category and label:
            qs = qs.filter(category=category, label=label)
        elif category:
            qs = qs.filter(category=category)
        elif label:
            qs = qs.filter(label=label)

        if query:
            lookups = (
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(info__icontains=query)
            )
            qs = qs.filter(lookups)
        return qs
    


class Detail(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializers
    lookup_field = 'pk'
    permission_classes = (permissions.AllowAny, )

    def get_related_items(self, item):
        related = Item.objects.filter(category=item.category).exclude(pk=item.pk)[:3]
        if related.count() < 3:
            additional_items_needed = 3 - related.count()
            additional_items = Item.objects.exclude(
                Q(category=item.category) | Q(pk=item.pk)
            )[:additional_items_needed]
            related = list(related) + list(additional_items)
        return related

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object() # Retrieve the Main Item
        related_items = self.get_related_items(instance) # Retrieve Related Items
        serializer = self.get_serializer(instance) # Serialize the Main Item
        data = serializer.data        
        data['related_items'] = ItemSerializers(related_items, many=True).data # Extend the Response Data
        return Response(data)
    
# WISH LIST VIEWS
class WishList(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializers

    def get_queryset(self):
        user = self.request.user
        qs = user.wish.all()

        return qs


@api_view(["POST"])
def add_wish(request, pk):
    try:
        post = Item.objects.get(pk=pk)
        if request.user in post.wish.all():
            post.wish.remove(request.user)
            return Response({'success': "Item remove from wish list", "wished": False})
        else:
            post.wish.add(request.user)
            return Response({'success': "Item added to wish list", "wished": True})
    except:
        return Response({"error": "error"})





@api_view(["GET"])
@csrf_protect
def cart_view(request, *args, **kwargs):
    try:
        # Attempt to retrieve the order for the current user with ordered=False
        order = Order.objects.get(user=request.user, ordered=False)
        cart_total = order.get_total()
        l = []
        for i in order.items.all():
            if i.item.discount_price:
                price = i.item.discount_price
            else:
                price = i.item.price

            id = i.item.id
            quantity = i.quantity
            name = i.item.title            
            total = i.get_final_price()
            pic = i.item.image.url
            context = {
                'id': id,
                'price': price,
                'quantity': quantity,
                'name': name,
                'pic': pic,
                'total': total,
            }
            l.append(context)
        
        serializer = CartItemSerializer(l, many=True).data
        serializer_data = {
            "cart_items": serializer,
            "cart_total": cart_total
        }
        return Response(serializer_data)
    except ObjectDoesNotExist:
        # Handle the case where no order is found

        return Response({"message": "No order exists for this user."}, status=status.HTTP_404_NOT_FOUND)





@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def add_to_cart(request, pk):
    item = get_object_or_404(Item, id=pk)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item quantity updated successfully!")
        else:
            order.items.add(order_item)
            messages.info(request, "Item added to your cart successfully!")
    else:
        order = Order.objects.create(user=request.user)
        order.items.add(order_item)
        messages.info(request, "Item added to your cart successfully!")
    return Response("store:order")



@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False,
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "this item was removed form the cart!")
        else:
            messages.info(request, "no order item")
            return Response({"message": "qs not found"})
    else:
        messages.info(request, "no order item")
        return Response({"message": "qs not found"})
    return Response({"massege": "success"})

@api_view(["POST", "GET"])
def remove_one_item_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False,
            )[0]

            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()

            else:
                order.items.remove(order_item)
                order_item.delete()
                order.save()
        else:
            return Response({"message": "failed order not found"})
    else:
        return Response({"message": "qs not found"})
            
    messages.info(request, "Item quantity updated successfully !")
    return Response({"massege": "success"})



class CheckoutView(generics.GenericAPIView):

    def post(self, *args, **kwargs):
        try:
            
            data = self.request.data
            user_ = self.request.user # user
            

            order = Order.objects.get(user=user_, shipping=False)
            
            billing_address = BillingAddress(
            user = user_,
            billing_order = order,
            address = data['address'],
            address2 = data['address2'],
            country = data['country'],
            region = data['region'],
            zip = data['zip'],
            )
            billing_address.save()
            order.billing_address=billing_address
            order.save()
            return Response({"massege": "success"})
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have any order !")
            return Response({"massege": "api failed"})


@csrf_exempt
@api_view(["GET"])
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@api_view(["POST"])
def oreder_ordered(request):
    order = Order.objects.get(user=request.user, ordered = False)
    for order_item in order.items.all():
        order_item.ordered = True
        order_item.save()
    order.ordered = True
    order.save()
    return Response({"massege": "api order success"})

@api_view(["POST", "GET"])
def payment_success(request):
    order = Order.objects.get(user=request.user, ordered=True, shipping = False)
    for order_item in order.items.all():
        order_item.shipping = True
        order_item.save()
    order.shipping = True
    order.save()
    return redirect("http://localhost:8000/")


def payment_cancel(request):
    return Response({"massege": "api order fail"})

@csrf_exempt
@api_view(["POST", "GET"])
def create_checkout_session(request):
    domain_url = 'http://localhost:8000/'
    stripe.api_key = settings.STRIPE_SECRET_KEY
    user = request.user
    order = Order.objects.get(user=user, ordered=True, shipping=False)
    total = order.get_total()
    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url+'payment_success/',  # Change this to your relative success URL
            cancel_url=domain_url+'/',    # Change this to your relative cancel URL
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': total * 100,
                    'product_data': {
                        'name': 'Cart Total',
                        'description': 'the total of the item in your cart',
                    },
                },
                'quantity': 1,
            }],
        )
        return JsonResponse({'sessionId': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)})
