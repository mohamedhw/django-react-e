from .models import Item, Order, OrderItem, BillingAddress
from django.contrib import messages
from django.shortcuts import get_object_or_404
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


class Home(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializers
    permission_classes = (permissions.AllowAny, )

class Detail(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializers
    lookup_field = 'pk'
    permission_classes = (permissions.AllowAny, )

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


class PostSearch(generics.ListAPIView):
    queryset =Item.objects.all()
    serializer_class= ItemSerializers

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('q')
        qs = Item.objects.search(query)
        # qs = ItemSerializer(qs)

        return qs


class CheckoutView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            order = Order.objects.get(user=request.user, ordered=False)
            form = CheckoutForm()
            context = {
                "form": form,
                "object": order,
            }
            return render(self.request, 'checkout-page.html', context)
        else:
            return redirect("users:login")
    def post(self, *args, **kwargs):
        try:
            
            data = self.request.data
            user_ = self.request.user # user
            

            order = Order.objects.get(user=user_, ordered=False)
            
            billing_address = BillingAddress(
            user = user_,
            billing_order = order,
            address = data['address'],
            address2 = data['address2'],
            country = data['country'],
            zip = data['zip'],
            )
            billing_address.save()
            order.billing_address=billing_address
            order.save()
            return Response({"massege": "success"})
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have any order !")
            return Response({"massege": "api failed"})
