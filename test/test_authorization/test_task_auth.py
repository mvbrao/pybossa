# -*- coding: utf8 -*-
# This file is part of PyBossa.
#
# Copyright (C) 2014 SF Isle of Man Limited
#
# PyBossa is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBossa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBossa.  If not, see <http://www.gnu.org/licenses/>.

from default import Test, assert_not_raises
from pybossa.auth import require
from nose.tools import assert_raises
from werkzeug.exceptions import Forbidden, Unauthorized
from mock import patch
from test_authorization import mock_current_user
from factories import AppFactory, UserFactory, TaskFactory
from pybossa.model.task import Task



class TestTaskAuthorization(Test):

    mock_anonymous = mock_current_user()
    mock_authenticated = mock_current_user(anonymous=False, admin=False, id=2)
    mock_admin = mock_current_user(anonymous=False, admin=True, id=1)



    @patch('pybossa.auth.current_user', new=mock_anonymous)
    def test_anonymous_user_cannot_crud(self):
        """Test anonymous users cannot crud tasks"""
        user = UserFactory.create()
        app = AppFactory.create(owner=user)
        task = TaskFactory.create(app=app)

        assert_raises(Unauthorized, require.ensure_authorized, 'create', task)
        assert_not_raises(Forbidden, require.ensure_authorized, 'read', task)
        assert_not_raises(Forbidden, require.ensure_authorized, 'read', Task)
        assert_raises(Unauthorized, require.ensure_authorized, 'update', task)
        assert_raises(Unauthorized, require.ensure_authorized, 'delete', task)


    @patch('pybossa.auth.current_user', new=mock_authenticated)
    def test_project_owner_can_crud(self):
        """Test project owner can crud tasks"""
        user = UserFactory.create()
        owner = UserFactory.create()
        app = AppFactory.create(owner=owner)
        task = TaskFactory.create(app=app)

        assert self.mock_authenticated.id == owner.id
        assert_not_raises(Forbidden, require.ensure_authorized, 'create', task)
        assert_not_raises(Forbidden, require.ensure_authorized, 'read', task)
        assert_not_raises(Forbidden, require.ensure_authorized, 'read', Task)
        assert_not_raises(Forbidden, require.ensure_authorized, 'update', task)
        assert_not_raises(Forbidden, require.ensure_authorized, 'delete', task)


    @patch('pybossa.auth.current_user', new=mock_authenticated)
    def test_not_project_owner_cannot_crud(self):
        """Test non owner user cannot crud tasks"""
        owner = UserFactory.create()
        non_owner = UserFactory.create()
        app = AppFactory.create(owner=owner)
        task = TaskFactory.create(app=app)

        assert self.mock_authenticated.id != owner.id
        assert_raises(Forbidden, require.ensure_authorized, 'create', task)
        assert_not_raises(Forbidden, require.ensure_authorized, 'read', task)
        assert_not_raises(Forbidden, require.ensure_authorized, 'read', Task)
        assert_raises(Forbidden, require.ensure_authorized, 'update', task)
        assert_raises(Forbidden, require.ensure_authorized, 'delete', task)


    @patch('pybossa.auth.current_user', new=mock_admin)
    def test_admin_can_crud(self):
        """Test admin user can crud tasks"""
        admin = UserFactory.create()
        owner = UserFactory.create()
        app = AppFactory.create(owner=owner)
        task = TaskFactory.create(app=app)

        assert self.mock_admin.id != owner.id
        assert_not_raises(Forbidden, require.ensure_authorized, 'create', task)
        assert_not_raises(Forbidden, require.ensure_authorized, 'read', task)
        assert_not_raises(Forbidden, require.ensure_authorized, 'read', Task)
        assert_not_raises(Forbidden, require.ensure_authorized, 'update', task)
        assert_not_raises(Forbidden, require.ensure_authorized, 'delete', task)
