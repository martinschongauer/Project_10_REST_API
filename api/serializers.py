from rest_framework import serializers

from api.models import User, Project, Contributor, Issue, Comment


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['title', 'description', 'type', 'author_user_id', 'id']


class CreateProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = ['title', 'description', 'type', 'author_user_id']


class ProjectDetailSerializer(serializers.ModelSerializer):

    project_issues = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['title', 'description', 'type', 'author_user_id', 'project_issues']

    def get_project_issues(self, instance):
        queryset = instance.project_issue.all()
        serializer = IssueSerializer(queryset, many=True)
        return serializer.data


class IssueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ['title', 'desc', 'tag', 'priority', 'status', 'author_user_id',
                  'assignee_user_id', 'project_id', 'created_time', 'id']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'id']


class ContributorSerializer(serializers.ModelSerializer):

    contributor_user = serializers.SerializerMethodField()

    class Meta:
        model = Contributor
        fields = ['role', 'permission', 'contributor_user']

    def get_contributor_user(self, instance):
        # queryset = instance.user_id.all()
        serializer = UserSerializer(instance.user_id)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['description', 'author_user_id', 'issue_id', 'created_time', 'id']


class CreateCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['description']


class UpdateCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['description']


#
# class ArticleSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Article
#         fields = ['id', 'date_created', 'date_updated', 'name', 'price', 'product']
#
#     def validate_price(self, value):
#         if value < 1:
#             raise serializers.ValidationError('Price must be greater than 1')
#         return value
#
#     def validate_product(self, value):
#         if value.active is False:
#             raise serializers.ValidationError('Inactive product')
#         return value
#
#
# class ProductListSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Product
#         fields = ['id', 'date_created', 'date_updated', 'name', 'category']
#
#
# class ProductDetailSerializer(serializers.ModelSerializer):
#
#     articles = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Product
#         fields = ['id', 'date_created', 'date_updated', 'name', 'category', 'articles']
#
#     def get_articles(self, instance):
#         queryset = instance.articles.filter(active=True)
#         serializer = ArticleSerializer(queryset, many=True)
#         return serializer.data
#
#
# class CategoryListSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Category
#         fields = ['id', 'date_created', 'date_updated', 'name', 'description']
#
#     def validate_name(self, value):
#         # Nous vérifions que la catégorie existe
#         if Category.objects.filter(name=value).exists():
#             # En cas d'erreur, DRF nous met à disposition l'exception ValidationError
#             raise serializers.ValidationError('Category already exists')
#         return value
#
#     def validate(self, data):
#         if data['name'] not in data['description']:
#             raise serializers.ValidationError('Name must be in description')
#         return data
#
#
# class CategoryDetailSerializer(serializers.ModelSerializer):
#
#     products = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Category
#         fields = ['id', 'date_created', 'date_updated', 'name', 'products']
#
#     def get_products(self, instance):
#         queryset = instance.products.filter(active=True)
#         serializer = ProductDetailSerializer(queryset, many=True)
#         return serializer.data
