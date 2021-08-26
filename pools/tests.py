from django.http import response
from django.test import TestCase
import datetime
from django.utils import timezone
from .models import Question
from django.urls import reverse

# Create your tests here.
class QuestionModelTests(TestCase):
  # was_published_recently()が未来の投稿をfalseで返すか確かめるテスト
  def test_was_published_recently_with_future_question(self):
    time = timezone.now() + datetime.timedelta(days=30)
    future_question = Question(pub_date=time)
    self.assertIs(future_question.was_published_recently(), False)

  # was_published_recently()が1日以上昔の投稿をfalseで返すか確かめるテスト
  def test_was_published_recently_with_old_question(self):
    time = timezone.now() - datetime.timedelta(days=1, seconds=1)
    old_question = Question(pub_date=time)
    self.assertIs(old_question.was_published_recently(), False)

  # was_published_recently()が最近の投稿をTrueで返すか確かめるテスト
  def test_was_published_recently_with_recent_question(self):
    time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
    recent_question = Question(pub_date=time)
    self.assertIs(recent_question.was_published_recently(), True)
    
# 上記のものは、models.pyのwas_published_recently()対するテストだった
# ここからは、投稿されるもの(views.pyのfilterの適用後)がきちんと投稿日以降が公開されるようになっているかの確認

# ダミーのQuestionと公開日時を決めたものを作る。
def create_question(question_text, days):
  time = timezone.now() + datetime.timedelta(days=days)
  return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
  # テストDBは毎回作り直されるので、空であることを確認する。
  def test_no_question(self):
    response = self.client.get(reverse('pools:index'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, "No pools are available")
    self.assertQuerysetEqual(response.context['latest_question_list'], [])

  # 30日前の投稿を作り、既に公開されていることを確かめる
  def test_past_question(self):
    create_question(question_text="Past question.", days=-30)
    response = self.client.get(reverse('pools:index'))
    self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

  # 30日後の投稿を作り、公開されていないことを確かめる
  def test_future_question(self):
    create_question(question_text="Future question.", days=30)
    response = self.client.get(reverse('pools:index'))
    self.assertContains(response, "No pools are available.")
    self.assertQuerysetEqual(response.context['latest_question_list'], [])

  # 過去と未来2つの投稿を作り、過去の投稿だけ公開されていることを確かめる
  def test_future_question_and_past_question(self):
    create_question(question_text="Past question.", days=-30)
    create_question(question_text="Future question.", days=30)
    response = self.client.get(reverse('pools:index'))
    self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

  # 過去の投稿を2つ作り、2つとも投稿されていることを確かめる
  def test_two_past_questions(self):
    create_question(question_text="Past question 1.", days=-30)
    create_question(question_text="Past question 2.", days=-5)
    response = self.client.get(reverse('pools:index'))
    self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question 2.>', '<Question: Past question 1.>'])


# detailのテスト
class QuestionDetailViewTests(TestCase):
  # 未来の投稿をした時、その質問は見つからないことを確認する
  def test_future_question(self):
    future_question = create_question(question_text='Future question.', days=5)
    url = reverse('pools:detail', args=(future_question.id,))
    response = self.client.get(url)
    self.assertEqual(response.status_code, 404)

  # 過去の投稿をした時、その投稿の文があることを確認する
  def test_past_question(self):
    past_question =create_question(question_text='Past question.', days=-5)
    url = reverse('pools:detail', args=(past_question.id,))
    response = self.client.get(url)
    self.assertContains(response, past_question.question_text)

