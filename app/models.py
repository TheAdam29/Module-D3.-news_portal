from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # cвязь «один к одному» с встроенной моделью пользователей User;
    rating_author = models.FloatField(default=0.0)  # рейтинг пользователя


    def update_rating(self):
        author_posts_rating = Post.objects.filter(author_id=self.pk).aggregate(r1=Coalesce(Sum('rating_post'), 0))['r1']
        author_comments_rating = Comment.objects.filter(userComment_id=self.user).aggregate(r2=Coalesce(Sum('rating_comment'), 0))['r2']
        author_posts_comment_rating = Comment.objects.filter(postComment__author__user=self.user).aggregate(r3=Coalesce(Sum('rating_comment'), 0))['r3']

        self.rating_author = author_posts_rating * 3 + author_comments_rating + author_posts_comment_rating
        self.save()


class Category(models.Model):
    name_category = models.CharField(max_length=64, unique=True)  # Категории новостей/статей


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)  # связь «один ко многим» с моделью Author
    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOICES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья')
    )
    categoryType = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)
    time_in = models.DateTimeField(auto_now_add=True)  # атоматически добавляемая дата и время создания
    category = models.ManyToManyField(Category, through='PostCategory')  # связь «многие ко многим» с моделью Category (с дополнительной моделью PostCategory)
    title = models.CharField(max_length=255)  # заголовок статьи/новости
    text_post = models.TextField()  # текст статьи/новости
    rating_post = models.IntegerField(default=0)  # рейтинг статьи/новости

    def __str__(self):
        return f'{self.title}'

    def like(self):
        self.rating_post += 1
        self.save()

    def dislike(self):
        self.rating_post -= 1
        self.save()

    def preview(self):
        return f'{self.text_post[:124]}...'


class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE) # связь «один ко многим» с моделью Post
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE) # связь «один ко многим» с моделью Category


class Comment(models.Model):
    postComment = models.ForeignKey(Post, on_delete=models.CASCADE) # связь «один ко многим» с моделью Post
    userComment = models.ForeignKey(User, on_delete=models.CASCADE) # связь «один ко многим» со встроенной моделью User (комментарии может оставить любой пользователь, необязательно автор)
    text_comment = models.TextField() # текст комментария
    time_create_comment = models.DateTimeField(auto_now_add=True) # дата и время создания комментария
    rating_comment = models.IntegerField(default=0) # рейтинг комментария

    def like(self):
        self.rating_comment += 1
        self.save()

    def dislike(self):
        self.rating_comment -= 1
        self.save()