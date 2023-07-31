"""
Questions:
 

    1. Complete the `MiniVenmo.create_user()` method to allow our application to create new users.

    2. Complete the `User.pay()` method to allow users to pay each other. Consider the following: if user A is paying user B, user's A balance should be used if there's enough balance to cover the whole payment, if not, user's A credit card should be charged instead.

    3. Venmo has the Feed functionality, that shows the payments that users have been doing in the app. If Bobby paid Carol $5, and then Carol paid Bobby $15, it should look something like this.
   

    Bobby paid Carol $5.00 for Coffee
    Carol paid Bobby $15.00 for Lunch

    Implement the `User.retrieve_activity()` and `MiniVenmo.render_feed()` methods so the MiniVenmo application can render the feed.

    4. Now users should be able to add friends. Implement the `User.add_friend()` method to allow users to add friends.
    5. Now modify the methods involved in rendering the feed to also show when user's added each other as friends.
"""

"""
MiniVenmo! Imagine that your phone and wallet are trying to have a beautiful
baby. In order to make this happen, you must write a social payment app.
Implement a program that will feature users, credit cards, and payment feeds.
"""

import re
import unittest
import uuid
from typing import Dict


class UsernameException(Exception):
    pass


class UsernameAlreadyExists(UsernameException):
    pass

class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class Payment:

    def __init__(self, amount, actor, target, note):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note


class User:

    def __init__(self, username):
        self._feed = list()
        self._friends = dict()
        self.credit_card_number = None
        self.balance = 0.0

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException('Username not valid.')


    def retrieve_feed(self):
        return self._feed

    def add_friend(self, new_friend):
        if new_friend.username not in self._friends:
            self._friends[new_friend.username] = new_friend
            new_friend.add_friend(self)
            self._feed.append(f"{self.username} adds {new_friend.username} as a friend")
            

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number
        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target, amount, note):
        if self.balance >= amount:
            self.pay_with_balance(target, amount, note)
        else:
            self.pay_with_card(target=target, amount=amount, note=note)
        self._feed.append(f"{self.username} paid {target.username} ${amount} for {note}")


    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def pay_with_balance(self, target, amount, note):
        self.balance -= amount
        target.add_to_balance(amount)

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match('^[A-Za-z0-9_\\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass


class MiniVenmo:
    _users: Dict[str, User]
    
    def __init__(self):
        self._users = dict()
    
    def create_user(self, username, balance, credit_card_number):
        if username in self._users:
            raise UsernameAlreadyExists
        new_user = User(username=username)
        new_user.add_to_balance(balance)
        new_user.add_credit_card(credit_card_number=credit_card_number)
        self._users[username] = new_user

    def render_feed(self, feed):
        for msg in feed:
            print(msg)

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")
 
            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)


class TestUser(unittest.TestCase):
    def setUp(self):
        self._minivenmo = MiniVenmo()

    def test_this_works(self):
        with self.assertRaises(UsernameException):
            raise UsernameException()
        
       
    def test_valid_user_created(self):
        self._minivenmo.create_user("Bobby", 34, "4111111111111111")
        self.assertTrue("Bobby" in self._minivenmo._users)
        self.assertEqual(self._minivenmo._users["Bobby"].username, "Bobby")
        self.assertEqual(self._minivenmo._users["Bobby"].balance, 34)
        self.assertEqual(self._minivenmo._users["Bobby"].credit_card_number, "4111111111111111")
        
    def test_repeated_username(self):
        self._minivenmo.create_user("Bobby", 34, "4111111111111111")
        with self.assertRaises(UsernameAlreadyExists):
            self._minivenmo.create_user("Bobby", 35, "4111111111111111")
            
    def test_wrong_card(self):
        with self.assertRaises(CreditCardException):
            self._minivenmo.create_user("Bobby", 35, "4111111111111256")
            
    def test_payment_with_balance(self):
        self._minivenmo.create_user("Bobby", 34, "4111111111111111")
        self._minivenmo.create_user("Bobby2", 100, "4242424242424242")
        user1 = self._minivenmo._users["Bobby"]
        user2 = self._minivenmo._users["Bobby2"]
        user1.pay(target=user2, amount=30, note="The stuff")
        self.assertEqual(user1.balance, 4)
        self.assertEqual(user2.balance, 130)
    
    def test_payment_with_credit_card(self):
        self._minivenmo.create_user("Bobby", 34, "4111111111111111")
        self._minivenmo.create_user("Bobby2", 100, "4242424242424242")
        user1 = self._minivenmo._users["Bobby"]
        user2 = self._minivenmo._users["Bobby2"]
        user1.pay(target=user2, amount=100, note="The stuff")
        self.assertEqual(user1.balance, 34)
        self.assertEqual(user2.balance, 200)
        
    def test_get_feed(self):
        self._minivenmo.create_user("Bobby", 34, "4111111111111111")
        self._minivenmo.create_user("Bobby2", 100, "4242424242424242")
        user1 = self._minivenmo._users["Bobby"]
        user2 = self._minivenmo._users["Bobby2"]
        user1.pay(target=user2, amount=100, note="Books")
        feed =user1.retrieve_feed()
        self.assertEqual(len(feed), 1)
        self.assertEqual(feed[0], "Bobby paid Bobby2 $100 for Books")

    def test_get_void_feed(self):
        self._minivenmo.create_user("Bobby", 34, "4111111111111111")
        self._minivenmo.create_user("Bobby2", 100, "4242424242424242")
        user1 = self._minivenmo._users["Bobby"]
        user2 = self._minivenmo._users["Bobby2"]
        self.assertFalse(user1.retrieve_feed())
        self.assertFalse(user2.retrieve_feed())

    def test_render(self):
        try:
            self._minivenmo.create_user("Bobby", 34, "4111111111111111")
            self._minivenmo.create_user("Bobby2", 100, "4242424242424242")
            user1 = self._minivenmo._users["Bobby"]
            user2 = self._minivenmo._users["Bobby2"]
            user1.pay(target=user2, amount=100, note="Books")
            feed =user1.retrieve_feed()
            self._minivenmo.render_feed(feed=feed)
        except Exception as e:
            self.fail("No Exception expected")
            
    def test_add_friend(self):
        self._minivenmo.create_user("Bobby", 34, "4111111111111111")
        self._minivenmo.create_user("Bobby2", 100, "4242424242424242")
        user1 = self._minivenmo._users["Bobby"]
        user2 = self._minivenmo._users["Bobby2"]
        user1.add_friend(user2)
        self.assertTrue(user1.username in user2._friends)
        self.assertTrue(user2.username in user1._friends)
        
    def test_add_friend_with_feed(self):
        self._minivenmo.create_user("Bobby", 34, "4111111111111111")
        self._minivenmo.create_user("Bobby2", 100, "4242424242424242")
        user1 = self._minivenmo._users["Bobby"]
        user2 = self._minivenmo._users["Bobby2"]
        user1.add_friend(user2)
        feed_user1 = user1.retrieve_feed()
        feed_user2 = user2.retrieve_feed()
        self.assertEqual(len(feed_user1), 1)
        self.assertEqual(len(feed_user2), 1)
        self.assertEqual(feed_user1[0], "Bobby adds Bobby2 as a friend")
        self.assertEqual(feed_user2[0], "Bobby2 adds Bobby as a friend")


if __name__ == '__main__':
    unittest.main()